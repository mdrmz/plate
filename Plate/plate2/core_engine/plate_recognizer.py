import os
import shutil
import re
import cv2
import pytesseract
import numpy as np


class PlateRecognizer:
    """
    Türk plakalarını daha sağlam şekilde tanımaya çalışır.
    - Geliştirilmiş ön işleme (CLAHE, bilateral, adaptive thresh)
    - Birden fazla OCR denemesi (normal, inverted, adaptive)
    - Konuma dayalı akıllı düzeltmeler (il kodu, harf grubu, son sayı grubu)
    - Basit skorlamaya dayalı en iyi sonucu seçer
    """

    def __init__(self, tesseract_path: str = None):
        """
        Eğer tesseract_path verilmişse orayı kullanır; değilse PATH'te arar.
        Bulunamazsa sadece uyarı verir (test ortamında lokal Tesseract yoksa hata fırlatma yerine uyarı).
        """
        try:
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                # Eğer sistem PATH'inde tesseract yoksa, windows varsayılan yolunu dene
                if not shutil.which("tesseract"):
                    default_win = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                    if os.path.exists(default_win):
                        pytesseract.pytesseract.tesseract_cmd = default_win
            # Basit sürüm kontrolü (hata verirse yakalanır)
            _ = pytesseract.get_tesseract_version()
        except Exception:
            # Tesseract bulunamazsa yalnızca uyarı veriyoruz; OCR çağrıları hata döndürebilir.
            print("UYARI: Tesseract bulunamadı veya erişilemedi. OCR çağrıları başarısız olabilir.")

    def _resize_keep_aspect(self, img, target_h=80):
        h, w = img.shape[:2]
        if h == 0: return img
        scale = max(1.0, target_h / float(h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    def _preprocess_image(self, plate_image):
        """
        Geliştirilmiş ön işleme:
        - Yeniden boyutlandırma (karakterleri büyütmek için)
        - CLAHE ile kontrast iyileştirme
        - Bilateral filtresiyle gürültü azaltma
        - Adaptive threshold ve morfolojik işlemler
        """
        if plate_image is None:
            return None
        if plate_image.size == 0:
            return None

        img = plate_image.copy()
        img = self._resize_keep_aspect(img, target_h=80)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # CLAHE ile kontrast artışı
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Gürültü azaltma ama kenarları koru
        gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # Adaptive threshold: değişken aydınlatma koşullarında iyi
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Küçük artefaktları temizle
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        return opened

    def _generate_variants(self, preproc_img):
        """
        OCR için birkaç varyant oluştur: orijinal, inverted, biraz açılmış/kapalı vb.
        """
        variants = []
        variants.append(preproc_img)
        try:
            inv = cv2.bitwise_not(preproc_img)
            variants.append(inv)
        except Exception:
            pass

        # Slightly dilate to join broken strokes (word-level improvement)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        dilated = cv2.dilate(preproc_img, kernel, iterations=1)
        variants.append(dilated)

        # Erode to separate birleşik karakterleri
        eroded = cv2.erode(preproc_img, kernel, iterations=1)
        variants.append(eroded)

        # Ensure uniqueness by hashing
        unique = []
        seen = set()
        for v in variants:
            key = v.tobytes()[:64]
            if key not in seen:
                unique.append(v)
                seen.add(key)
        return unique

    def _clean_ocr_text(self, raw_text: str) -> str:
        if not raw_text:
            return ""
        # Remove non-alphanumeric but keep Turkish letters (ÇĞİÖŞÜ)
        cleaned = re.sub(r'[^A-Za-z0-9ÇĞİÖŞÜçğıöşü]', '', raw_text)
        cleaned = cleaned.upper()
        # Normalize Turkish letters to their uppercase proper forms (already upper)
        return cleaned

    def _post_process_text(self, text: str) -> str:
        """
        Konuma dayalı düzeltme algoritması (daha sağlam):
        1) İlk iki karakter il kodu olmalı -> rakam
        2) Orta bölüm harf olmalı -> harf (1-3)
        3) Son bölüm rakam olmalı -> 2-4 rakam
        Harf/rakam karışıklıkları için akıllı harita uygulanır.
        """
        if not text:
            return ""

        s = re.sub(r'[^A-Z0-9ÇĞİÖŞÜ]', '', text.upper())

        # Harita: OCR'ın karıştırdığı karakterler
        digit_to_letter_map = {'0': 'O', '1': 'I', '5': 'S', '8': 'B', '2': 'Z', '6': 'G'}
        letter_to_digit_map = {'O': '0', 'Q': '0', 'D': '0', 'I': '1', 'L': '1', 'Z': '2',
                               'S': '5', 'B': '8', 'G': '6'}

        # Eğer çok kısa ise return direkt (ama temizlenmiş)
        if len(s) < 4:
            return s

        char_list = list(s)

        # 1) İlk iki karakter -> rakam olacak şekilde düzelt
        for i in range(2):
            if i >= len(char_list):
                break
            c = char_list[i]
            if not c.isdigit():
                if c in letter_to_digit_map:
                    char_list[i] = letter_to_digit_map[c]
                else:
                    # Bazı durumlarda ilk char tek olarak rakam yerine harf okunmuşsa
                    # örn. 'S4' gibi, zor durumda bırakıyoruz (uygulama seviyesinde ele alınabilir)
                    pass

        # 2) Son bölümde (son 2..4 char) rakam olmalı
        # Guess how many trailing digits: try 2,3,4 and pick the one that gives valid middle length
        best_candidate = None

        def candidate_from_list(cl):
            return "".join(cl)

        # We'll try possible splits: first 2 digits fixed, last_len in [2,3,4]
        first_part = "".join(char_list[:2]) if len(char_list) >= 2 else "".join(char_list)
        remainder = "".join(char_list[2:])

        for last_len in (4, 3, 2):
            if len(remainder) < last_len:
                continue
            mid = list(remainder[:-last_len]) if last_len <= len(remainder) else []
            tail = list(remainder[-last_len:])
            # Fix tail to digits
            for idx in range(len(tail)):
                if not tail[idx].isdigit():
                    if tail[idx] in letter_to_digit_map:
                        tail[idx] = letter_to_digit_map[tail[idx]]
                    else:
                        # If letter where digit expected and no mapping, try to coerce common ones
                        if tail[idx] in ('O', 'Q', 'D'):
                            tail[idx] = '0'
            # Fix middle to letters
            for idx in range(len(mid)):
                if mid[idx].isdigit():
                    if mid[idx] in digit_to_letter_map:
                        mid[idx] = digit_to_letter_map[mid[idx]]
                    else:
                        # If digit remains in middle and no mapping, try to leave it (rare)
                        pass

            cand = first_part + "".join(mid) + "".join(tail)
            # Validate format roughly: first 2 digits, mid 1-3 letters, tail 2-4 digits
            if re.match(r'^\d{2}[A-ZÇĞİÖŞÜ]{1,3}\d{2,4}$', cand):
                best_candidate = cand
                break

        # If none matched, try a looser correction: enforce first two digits and convert remaining letter-like/digit-like using maps
        if not best_candidate:
            cl = char_list[:]
            # enforce tail digits (last up to 4)
            for i in range(len(cl) - 1, max(-1, len(cl) - 5), -1):
                if not cl[i].isdigit() and cl[i] in letter_to_digit_map:
                    cl[i] = letter_to_digit_map[cl[i]]
            # enforce middle letters for indices 2..len-3
            for i in range(2, max(2, len(cl) - 2)):
                if cl[i].isdigit() and cl[i] in digit_to_letter_map:
                    cl[i] = digit_to_letter_map[cl[i]]
            cand = "".join(cl)
            # Final regex check
            if re.match(r'^\d{2}[A-ZÇĞİÖŞÜ]{1,3}\d{2,4}$', cand):
                best_candidate = cand

        final = best_candidate if best_candidate else "".join(char_list)

        # Normalize Turkish chars to ASCII equivalents for DB compatibility
        char_map = str.maketrans("ÇĞİÖŞÜ", "CGIOSU")
        final_ascii = final.translate(char_map)

        # Final cleanup - uppercase and remove unexpected symbols
        final_ascii = re.sub(r'[^A-Z0-9]', '', final_ascii.upper())

        # Accept only if plausible length and starts with digit
        if re.match(r'^\d{2}[A-Z]{1,3}\d{2,4}$', final_ascii):
            return final_ascii

        return final_ascii  # caller may still decide based on score

    def _score_candidate(self, cand: str):
        """
        Basit skor: regex uyumu + uzunluk uygunluğu
        Regex tam uyanlara yüksek puan ver.
        """
        if not cand:
            return 0
        score = 0
        if re.match(r'^\d{2}[A-Z]{1,3}\d{2,4}$', cand):
            score += 100
        # length closeness to typical plate (min 6 max 9)
        if 6 <= len(cand) <= 9:
            score += 10
        # prefer starts with digit
        if cand and cand[0].isdigit():
            score += 5
        return score

    def recognize(self, plate_image):
        """
        Verilen plaka görüntüsünden en iyi tahmini döndürür veya None.
        """
        if plate_image is None or getattr(plate_image, "size", None) == 0:
            return None

        pre = self._preprocess_image(plate_image)
        if pre is None:
            return None

        variants = self._generate_variants(pre)

        # Tesseract config: tek satır (psm 7) ve Türkçe eğitim verisi
        whitelist = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ0123456789"
        config = f"--psm 7 -l tur -c tessedit_char_whitelist={whitelist}"

        best = None
        best_score = -1

        for var in variants:
            try:
                raw = pytesseract.image_to_string(var, config=config)
            except Exception:
                raw = ""
            cleaned = self._clean_ocr_text(raw)
            post = self._post_process_text(cleaned)

            # Score candidate
            score = self._score_candidate(post)

            # If multiple variants produce same candidate, prefer the one from original variant (no-op)
            if score > best_score:
                best_score = score
                best = post

            # Also try a more permissive OCR mode for difficult images (psm 6 or psm 11)
            try:
                raw2 = pytesseract.image_to_string(var, config=config.replace("--psm 7", "--psm 11"))
            except Exception:
                raw2 = ""
            cleaned2 = self._clean_ocr_text(raw2)
            post2 = self._post_process_text(cleaned2)
            score2 = self._score_candidate(post2) - 1  # prefer psm7 slightly
            if score2 > best_score:
                best_score = score2
                best = post2

        # Son kontrol: best uygun formata uyuyorsa döndür
        if best and re.match(r'^\d{2}[A-Z]{1,3}\d{2,4}$', best):
            return best

        # Eğer yukarıdaki katı regex başarısızsa, yine de plausiblity skoru yüksekse döndür
        if best and best_score >= 50 and 6 <= len(best) <= 9 and best[0].isdigit():
            return best

        return None