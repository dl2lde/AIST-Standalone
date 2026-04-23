#####################################################
# AIST – Version 2.0        #
# AstroImage Tools Suite / AstroImage Stretch Tool  #
# Author: Lucas Vuescu - © 2026                     #
# Contact: astro@mdci.ro or ldvuescu@gmail.com      #
#####################################################
#                                                   #
#   SPDX-License-Identifier: GPL-3.0-or-later       #
#                                                   #
#####################################################

import sys
import cv2
import os
import numpy as np
from astropy.io import fits
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QWidget, QSlider, QGridLayout, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap



class AST(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lucas - AstroImage Stretch Tool (AIST)")
        self.resize(1400, 720)

        self.image = None
        self.image_path = None

        # === IMAGE LABELS ===
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(400, 400)

        self.processed_label = QLabel()
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(400, 400)

        # === HISTOGRAM ===
        self.hist_label = QLabel()
        self.hist_label.setMinimumHeight(100)

        # === BUTTONS ===
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        self.save_btn = QPushButton("Save Image")
        self.save_btn.clicked.connect(self.save_image)

        self.brand_label = QLabel("© 2026 by Lucas V. - AstroImage Stretch Tool - v2.0")
        self.brand_label.setAlignment(Qt.AlignCenter)

        # === SLIDERS ===
        self.black_slider = QSlider(Qt.Horizontal)
        self.black_slider.setRange(0, 100)
        self.black_slider.setValue(0)

        self.mid_slider = QSlider(Qt.Horizontal)
        self.mid_slider.setRange(1, 100)
        self.mid_slider.setValue(32)

        self.white_slider = QSlider(Qt.Horizontal)
        self.white_slider.setRange(1, 100)
        self.white_slider.setValue(100)
        
        # 🔥 NEW SLIDERS
        self.enhance_slider = QSlider(Qt.Horizontal)
        self.enhance_slider.setRange(0, 100)
        self.enhance_slider.setValue(50)

        self.bg_slider = QSlider(Qt.Horizontal)
        self.bg_slider.setRange(0, 100)
        self.bg_slider.setValue(35)
        
        self.highlight_slider = QSlider(Qt.Horizontal)
        self.highlight_slider.setRange(0, 200)
        self.highlight_slider.setValue(5)
        
        self.autostretch_slider = QSlider(Qt.Horizontal)
        self.autostretch_slider.setRange(1, 99)   # 1 → 0.01, 95 → 0.95
        self.autostretch_slider.setValue(65)      # valoare default (0.65)

        # === VALUE LABELS ===
        self.black_value = QLabel("0")
        self.mid_value = QLabel("1.00")
        self.white_value = QLabel("100")
        self.autostretch_value = QLabel("0.65")

# for s in [self.black_slider, self.mid_slider, self.white_slider]:
        for s in [
            self.black_slider,
            self.mid_slider,
            self.white_slider,
            self.enhance_slider,
            self.bg_slider,
            # self.highlight_slider,
            self.autostretch_slider
        ]:
            s.valueChanged.connect(self.update_preview)
            s.valueChanged.connect(self.update_values)

        # === CHECKBOX ===
        self.auto_wb = QCheckBox("Auto WB")
        self.auto_wb.setChecked(True)
        self.auto_wb.stateChanged.connect(self.update_preview)

        self.auto_stretch = QCheckBox("Auto Stretch")
        self.auto_stretch.setChecked(True)
        self.auto_stretch.stateChanged.connect(self.update_preview)

        self.stf_cb = QCheckBox("STF")
        self.stf_cb.setChecked(True)
        self.stf_cb.stateChanged.connect(self.update_preview)

        # === LAYOUT ===
        image_layout = QHBoxLayout()
        image_layout.setSpacing(10)
        image_layout.setContentsMargins(5, 5, 5, 5)

        left = QVBoxLayout()
        left.addWidget(self.original_label)
        left.addWidget(self.load_btn)

        right = QVBoxLayout()
        right.addWidget(self.processed_label)
        right.addWidget(self.save_btn)
        
        image_layout.addLayout(left)
        image_layout.addLayout(right)

        sliders = QGridLayout()

        sliders.addWidget(QLabel("Black"), 0, 0)
        sliders.addWidget(self.black_slider, 0, 1)
        sliders.addWidget(self.black_value, 0, 2)

        sliders.addWidget(QLabel("Mid"), 1, 0)
        sliders.addWidget(self.mid_slider, 1, 1)
        sliders.addWidget(self.mid_value, 1, 2)

        sliders.addWidget(QLabel("White"), 2, 0)
        sliders.addWidget(self.white_slider, 2, 1)
        sliders.addWidget(self.white_value, 2, 2)

        sliders.addWidget(QLabel("Enhance"), 3, 0)
        sliders.addWidget(self.enhance_slider, 3, 1)

        sliders.addWidget(QLabel("Background"), 4, 0)
        sliders.addWidget(self.bg_slider, 4, 1)
        
        # 🔥 NEW UI
        # sliders.addWidget(QLabel("Highlight Protect"), 5, 0)
        # sliders.addWidget(self.highlight_slider, 5, 1)
        
        sliders.addWidget(QLabel("Stretch Factor"), 5, 0)
        sliders.addWidget(self.autostretch_slider, 5, 1)
        sliders.addWidget(self.autostretch_value, 5, 2)

        sliders.addWidget(self.auto_wb, 6, 0)
        sliders.addWidget(self.auto_stretch, 6, 1)
        sliders.addWidget(self.stf_cb, 6, 4)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addLayout(image_layout)
        main_layout.addWidget(self.hist_label)
        main_layout.addWidget(self.brand_label)
        main_layout.addLayout(sliders)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.apply_style()
        self.update_values()

    # ===== STYLE =====
    def apply_style(self):
        self.setStyleSheet("""
        QWidget { background-color: #1b1b1b; color: #cccccc; }

        QPushButton {
            background-color: #2a2a2a;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px;
        }

        QPushButton:hover { border: 1px solid #2ec4c7; }

        QSlider::groove:horizontal { height: 6px; background: #444; }

        QSlider::handle:horizontal {
            background: #2ec4c7;
            width: 12px;
            margin: -5px 0;
        }

        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 1px solid #2ec4c7;
            background-color: #1b1b1b;
        }

        QCheckBox::indicator:checked {
            background-color: #2ec4c7;
        }
        """)

        self.brand_label.setStyleSheet("color: #2ec4c7; font-style: italic; font-size: 18px;")

    # ===== VALUES =====
    def update_values(self):
        gamma = max(0.1, self.mid_slider.value() / 50.0)

        self.black_value.setText(str(self.black_slider.value()))
        self.mid_value.setText(f"{gamma:.2f}")
        self.white_value.setText(str(self.white_slider.value()))
        f = self.autostretch_slider.value() / 100.0
        self.autostretch_value.setText(f"{f:.2f}")

    # ===== STF =====
    def auto_stf(self, img):
        img = img.astype(np.float32)

        p1 = np.percentile(img, 0.2)
        p2 = np.percentile(img, 99.65)

        img = (img - p1) / (p2 - p1 + 1e-6)
        img = np.clip(img, 0, 1)

        img = np.power(img, 0.6)

        return (img * 255).astype(np.uint8)

    # ===== AUTO WB =====
    def auto_white_balance(self, img):
        b, g, r = cv2.split(img.astype(np.float32))
        
        avg = (np.mean(b) + np.mean(g) + np.mean(r)) / 3.0

        b *= avg / (np.mean(b) + 1e-6)
        g *= avg / (np.mean(g) + 1e-6)
        r *= avg / (np.mean(r) + 1e-6)
       
        return cv2.merge([b, g, r])
    # ===== STRETCH (CORE FIX) =====
    def stretch(self, img):
        img = img.astype(np.float32)
        auto_factor = self.autostretch_slider.value() / 100.0

        if self.auto_stretch.isChecked():
            f = self.autostretch_slider.value() / 100.0   # 0.01–0.95

            black = np.percentile(img, 0.25)
            white = np.percentile(img, 99 + f)
        else:
            black = self.black_slider.value()/100 * np.max(img)
            white = self.white_slider.value()/100 * np.max(img)

        gamma = max(0.1, self.mid_slider.value()/50.0)

        # normalize
        img = (img - black) / (white - black + 1e-6)
        img = np.clip(img, 0, 1)

        # 🔥 luminance stretch (important)
        luma = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        l = luma / (luma + (1.0 - luma) * gamma)

        img = img * (l[..., None] / (luma[..., None] + 1e-6))
        img = np.clip(img, 0, 1)

        # highlight protect
        k = self.highlight_slider.value()/100.0
        if k > 0:
            img = img / (1.0 + k * img)

        return np.clip(img, 0, 1)

 
    # ===== BACKGROUND ===== 
    def apply_background(self, img):
        val = self.bg_slider.value()
        if val == 0:
            return img
        strength = (val/100)**1.5
        bg = np.percentile(img,20,axis=(0,1))
        img = img - bg*strength
        return np.clip(img,0,1)

    # ===== ENHANCE =====
    def apply_enhance(self, img):
        val = self.enhance_slider.value()
        if val == 0:
            return img
        strength = (val/100)**1.5
        blur = cv2.GaussianBlur(img,(0,0),2)
        img = cv2.addWeighted(img,1+0.4*strength,blur,-0.4*strength,0)

        luma = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        luma = np.clip(luma, 0, None)
        sat = 1 + 0.3 * strength * np.sqrt(luma)
        # sat = 1 + 0.3*strength*(luma**0.5)
        img = img * sat[...,None]

        return np.clip(img,0,1)

    # ===== HISTOGRAM =====
    def draw_histogram(self, img):
        hist_img = np.zeros((150, 300, 3), dtype=np.uint8)

        for i, col in enumerate([(255,0,0),(0,255,0),(0,0,255)]):
            hist = cv2.calcHist([img],[i],None,[256],[0,256])
            hist = cv2.normalize(hist, hist).flatten()

            for x in range(1,256):
                cv2.line(hist_img,
                         (x-1, 150-int(hist[x-1]*150)),
                         (x, 150-int(hist[x]*150)),
                         col, 1)

        return hist_img

    # ===== LOAD (FITS UNIVERSAL) =====
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.tif *.tiff *.png *.jpg *.fit *.fits *.fts)"
        )
        if not file_path:
            return

        self.current_file = file_path

        # ===== FITS / FIT / FTS =====
        if file_path.lower().endswith((".fit", ".fits", ".fts")):
            hdul = fits.open(file_path)
            data = hdul[0].data.astype(np.float32)
            hdul.close()

            # Asigură-te că forma este (H,W,3)
            if data.ndim == 3 and data.shape[0] == 3:
                data = np.transpose(data, (1,2,0))

            if data.ndim == 2:
                data = np.stack([data]*3, axis=-1)

            self.image = data
            self.update_preview()
            return

        # ===== TIFF / PNG / JPG =====
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        # Convert to float32
        img = img.astype(np.float32)

        #TIFF 16-bit → normalizare corectă
        if img.dtype == np.uint16:
            img = img / 65535.0
        else:
            img = img / 255.0

        # Dacă este grayscale → convertim la RGB
        if img.ndim == 2:
            img = np.stack([img, img, img], axis=-1)

        # Dacă are 4 canale (BGRA) → eliminăm alfa
        if img.shape[2] == 4:
            img = img[:, :, :3]

        # Convertim BGR → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.image = img
        self.update_preview()

    # ===== SAVE (FITS UNIVERSAL) =====
    def save_image(self):
        if self.image is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "astro_result.tif",
            "TIFF (*.tif);;PNG (*.png);;JPG (*.jpg);;FITS (*.fits *.fit)"
        )

        if not path:
            return

        img = self.process_pipeline(self.image)
        img = np.clip(img, 0, 1)
        img = np.nan_to_num(img, nan=0.0, posinf=1.0, neginf=0.0)

        if path.lower().endswith((".fit", ".fits", ".fts")):
            rgb_fits = np.transpose(img, (2, 0, 1))   # (H,W,3) → (3,H,W)
            fits.PrimaryHDU(rgb_fits.astype(np.float32)).writeto(path, overwrite=True)
            return

        # PNG / JPG (8-bit)
        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            img8 = (img * 255).astype(np.uint8)
            img8 = cv2.cvtColor(img8, cv2.COLOR_BGR2RGB)
            cv2.imwrite(path, img8)
            return

        # TIFF (16-bit)
        img16 = (img * 65535).astype(np.uint16)
        img16 = cv2.cvtColor(img16, cv2.COLOR_BGR2RGB)
        cv2.imwrite(path, img16)




    def process_pipeline(self, img):
        img = img.astype(np.float32)
        if self.auto_wb.isChecked():
            img = self.auto_white_balance(img)
        img = self.stretch(img)
        img = self.apply_background(img)
        img = self.apply_enhance(img)
        return img

    def update_preview(self):
        if self.image is None:
            return

        if self.stf_cb.isChecked():
            preview = self.auto_stf(self.image)
        else:
            preview = self.image.copy()
            if preview.dtype != np.uint8:
                preview = cv2.normalize(preview, None, 0, 255, cv2.NORM_MINMAX)
                preview = preview.astype(np.uint8)

        proc = self.process_pipeline(self.image)
        proc = np.nan_to_num(proc, nan=0.0, posinf=1.0, neginf=0.0)
        proc8 = (proc * 255).astype(np.uint8)

        self.display(self.original_label, preview)
        self.display(self.processed_label, proc8)

        hist = self.draw_histogram(proc8)
        self.display(self.hist_label, hist)

    # ===== DISPLAY =====
    def display(self, label, img):
        if self.current_file.lower().endswith((".fit", ".fits", ".fts")):
            rgb = img.copy()   # FITS este deja RGB
        else:          
            rgb = img.copy()
            # rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # TIFF/PNG/JPG sunt BGR
        h, w, ch = rgb.shape

        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        pixmap = pixmap.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AST()
    w.show()
    sys.exit(app.exec())