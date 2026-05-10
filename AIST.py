#####################################################
# AIST – Version 3.0                                #
# AstroImage Tools Suite / AstroImage Stretch Tool  #
# Author: Lucas Vuescu - © 2026                     #
# Contact: astro@mdci.ro                            #
#####################################################
#                                                   #
#   SPDX-License-Identifier: GPL-3.0-or-later       #
#                                                   #
#####################################################

import sys
import os
import cv2
import numpy as np
import webbrowser
from astropy.io import fits

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


class AIMaster(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AstroImage Stretch Tool - v. 3.0")
        self.resize(1400, 720)
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # ===== CORE =====
        self.image = None
        self.original_image = None
        self.preview_image = None
        self.preview_scale = 0.20

        # ===== VIEWPORT =====
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None

        # ===== LABELS =====
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(300, 225)

        self.processed_label = QLabel()
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(800, 600)

        # === HISTOGRAM ===
        self.hist_label = QLabel()
        self.hist_label.setMinimumHeight(100)

        # === BUTTONS ===
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        self.save_btn = QPushButton("Save Image")
        self.save_btn.clicked.connect(self.save_image)

        self.brand_label = QLabel("AstroImage Stretch Tool PRO")
        self.brand_label.setAlignment(Qt.AlignCenter)
        
        self.subtitle_label = QLabel("release 3.0 - @2026 by Lucas V.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)


        # === SLIDERS ===
        self.black_slider = QSlider(Qt.Horizontal)
        self.black_slider.setRange(0, 100)
        self.black_slider.setValue(0)

        self.mid_slider = QSlider(Qt.Horizontal)
        self.mid_slider.setRange(1, 100)
        self.mid_slider.setValue(50)

        self.white_slider = QSlider(Qt.Horizontal)
        self.white_slider.setRange(1, 100)
        self.white_slider.setValue(100)
        
        # 🔥 NEW SLIDERS
        self.enhance_slider = QSlider(Qt.Horizontal)
        self.enhance_slider.setRange(0, 100)
        self.enhance_slider.setValue(30)

        self.bg_slider = QSlider(Qt.Horizontal)
        self.bg_slider.setRange(0, 100)
        self.bg_slider.setValue(35)
        
        self.highlight_slider = QSlider(Qt.Horizontal)
        self.highlight_slider.setRange(10, 100)
        self.highlight_slider.setValue(20)
        
        self.autostretch_slider = QSlider(Qt.Horizontal)
        self.autostretch_slider.setRange(1, 99)   # 1 → 0.01, 95 → 0.95
        self.autostretch_slider.setValue(75)      # valoare default (0.75)

        # === VALUE LABELS ===
        self.black_value = QLabel("0")
        self.mid_value = QLabel("1.00")
        self.white_value = QLabel("100")
        self.autostretch_value = QLabel("0.75")
        self.highlight_value = QLabel("0.20")

# for s in [self.black_slider, self.mid_slider, self.white_slider]:
        for s in [
            self.black_slider,
            self.mid_slider,
            self.white_slider,
            self.enhance_slider,
            self.bg_slider,
            self.highlight_slider,
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
        
        sliders = QGridLayout()

        sliders.addWidget(QLabel("Black"), 0, 0)
        sliders.addWidget(self.black_slider, 0, 1)
        sliders.addWidget(self.black_value, 0, 2)


        sliders.addWidget(QLabel("Middle"), 1, 0)
        sliders.addWidget(self.mid_slider, 1, 1)
        sliders.addWidget(self.mid_value, 1, 2)

        sliders.addWidget(QLabel("White"), 2, 0)
        sliders.addWidget(self.white_slider, 2, 1)
        sliders.addWidget(self.white_value, 2, 2)

        sliders.addWidget(QLabel("Enhance"), 3, 0)
        sliders.addWidget(self.enhance_slider, 3, 1)

        sliders.addWidget(QLabel("Background"), 4, 0)
        sliders.addWidget(self.bg_slider, 4, 1)
        
        sliders.addWidget(QLabel("Highlight Protect"), 5, 0)
        sliders.addWidget(self.highlight_slider, 5, 1)

        sliders.addWidget(QLabel("Stretch Factor"), 6, 0)
        sliders.addWidget(self.autostretch_slider, 6, 1)
        sliders.addWidget(self.autostretch_value, 6, 2)

        # ===== UI SPLIT =====
        
        # LEFT
        left_container = QWidget()
        left = QVBoxLayout(left_container)

        self.original_label.setMaximumHeight(300)

        left.addWidget(self.brand_label)
        left.addWidget(self.subtitle_label)
        
        left.addSpacing(10)
        left.addWidget(self.original_label)
        left.addSpacing(10)
        left.addLayout(sliders)
        left.addSpacing(10)
        left.addWidget(self.hist_label)
        left.addSpacing(10)
        cb_row = QHBoxLayout()
        cb_row.addWidget(self.auto_wb)
        cb_row.addWidget(self.auto_stretch)
        cb_row.addWidget(self.stf_cb)

        left.addLayout(cb_row)
        left.addStretch()

        left_container.setFixedWidth(300)
        

        # ===== RIGHT PANEL =====
        right = QVBoxLayout()

        # ===== TOOLBAR =====
        tb = QHBoxLayout()
        
        tb.addStretch()
        # hint text
        lbl_hint = QLabel("Zoom: Left Click (+) | Right Click (-) | Double Click = Reset | Shift + Drag = Pan")
        lbl_hint.setAlignment(Qt.AlignCenter)
        lbl_hint.setStyleSheet("""
        color: #00ffcc;
        font-size: 12pt;
        font-style: italic;
        """)

        # coffee button
        self.btn_coffee = QPushButton("☕")
        self.btn_coffee.setObjectName("CoffeeButton")
        self.btn_coffee.setToolTip("Buy me a coffee ☕")
        self.btn_coffee.setCursor(Qt.PointingHandCursor)

        import webbrowser
        self.btn_coffee.clicked.connect(
            lambda: webbrowser.open("https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=ldvuescu@gmail.com&currency_code=EUR&amount=5")
        )

        # ===== ADD IN TOOLBAR =====

        # tb.addSpacing(80)
        tb.addWidget(lbl_hint)

        tb.addStretch()

        tb.addWidget(self.btn_coffee)
        right.addLayout(tb)

        # preview
        self.processed_label.setMouseTracking(True)
        self.processed_label.mousePressEvent = self.mouse_press
        self.processed_label.mouseMoveEvent = self.mouse_move
        self.processed_label.mouseReleaseEvent = self.mouse_release
        self.processed_label.mouseDoubleClickEvent = self.mouse_double_click

        right.addWidget(self.processed_label)

        # bottom
        bottom = QHBoxLayout()
        # ===== ACTION BUTTONS =====
        self.apply_btn = QPushButton("Apply")
        self.reset_btn = QPushButton("Reset")

        self.apply_btn.clicked.connect(self.apply_changes)
        self.reset_btn.clicked.connect(self.reset_image)
        left_btns = QHBoxLayout()
        left_btns.addWidget(self.load_btn)
        left_btns.addWidget(self.save_btn)

        right_btns = QHBoxLayout()
        right_btns.addWidget(self.apply_btn)
        right_btns.addWidget(self.reset_btn)

        bottom.addLayout(left_btns)
        bottom.addStretch()
        bottom.addLayout(right_btns)

        right.addLayout(bottom)

        # ===== MAIN =====
        main = QHBoxLayout()
        main.addWidget(left_container, 3)
        main.addLayout(right, 7)

        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

        self.apply_style()

    # ===== STYLE =====
    def apply_style(self):
        self.setStyleSheet("""
        QWidget { background-color: #0b0f1a; color: #cccccc; }
        QPushButton {
            background-color: #0b0f1a;
            border: 1px solid #804040;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton:hover { background-color: #00994d; }
        QPushButton#ProcessButton { background-color: #0b0f1a; border: 1px solid #804040; }
        QPushButton#ProcessButton:hover { background-color: #00994d; }
        QPushButton#CloseButton { background-color: #0b0f1a; border: 1px solid #804040; }
        QPushButton#CloseButton:hover { background-color: #00994d; }

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
            background-color: #0b0f1a;
        }
        QCheckBox::indicator:checked {
            background-color: #2ec4c7;
        }
        """)

        self.brand_label.setStyleSheet("""
        color: #2ec4c7;
        font-size: 18px;
        font-weight: bold;
        font-family: "Segoe UI";
        """)

        self.subtitle_label.setStyleSheet("""
        color: #00ffbb;
        font-size: 12px;
        font-style: italic;
        """)
    # ===== VALUES =====
    def update_values(self):
        gamma = max(0.1, self.mid_slider.value() / 50.0)

        self.black_value.setText(str(self.black_slider.value()))
        self.mid_value.setText(f"{gamma:.2f}")
        self.white_value.setText(str(self.white_slider.value()))
        f = self.autostretch_slider.value() / 100.0
        self.autostretch_value.setText(f"{f:.2f}")
        k = self.highlight_slider.value() / 100.0
        self.highlight_value.setText(f"{k:.2f}")

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

        if self.auto_stretch.isChecked():

            f = self.autostretch_slider.value() / 100.0

            black = np.percentile(img, 0.25)
            white = np.percentile(img, 99 + f)

        else:

            black = self.black_slider.value() / 100.0 * np.max(img)
            white = self.white_slider.value() / 100.0 * np.max(img)

        gamma = max(0.1, self.mid_slider.value() / 50.0)

        # normalize
        img = (img - black) / (white - black + 1e-6)
        img = np.clip(img, 0, 1)

        # -------------------------------------------------
        # Hyperbolic Stretch
        # -------------------------------------------------

        luma = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        D = 1.25 * gamma

        stretch = np.arcsinh(D * luma) / np.arcsinh(D)

        # subtle tonal blend
        blend = 0.82

        l = luma * (1.0 - blend) + stretch * blend

        img = img * (l[..., None] / (luma[..., None] + 1e-6))

        img = np.clip(img, 0, 1)

        # -------------------------------------------------
        # Star Core Recovery
        # -------------------------------------------------

        k = np.clip(self.highlight_slider.value() / 100.0, 0.0, 1.0)

        if k > 0:

            eps = 1e-6

            luma = cv2.cvtColor(
                np.clip(img, 0, 1).astype(np.float32),
                cv2.COLOR_RGB2GRAY
            )

            luma = np.clip(luma, 0.0, 1.0)

            # ONLY highlights
            mask = np.clip((luma - 0.55) / 0.45, 0, 1)

            # smooth transition
            mask = mask ** (1.8 - 1.2 * k)

            r_ratio = img[..., 0] / np.maximum(luma, eps)
            g_ratio = img[..., 1] / np.maximum(luma, eps)
            b_ratio = img[..., 2] / np.maximum(luma, eps)

            r = luma * (r_ratio * (1.0 - mask) + mask)
            g = luma * (g_ratio * (1.0 - mask) + mask)
            b = luma * (b_ratio * (1.0 - mask) + mask)

            recovered = np.stack([r, g, b], axis=-1)

            # controlled blend
            recovery_blend = 0.35 * k

            img = img * (1.0 - recovery_blend) + recovered * recovery_blend

            # subtle highlight compression
            compression = 1.0 - (0.03 * k)

            img = np.power(img, compression)

            img = np.nan_to_num(
                img,
                nan=0.0,
                posinf=1.0,
                neginf=0.0
            )

            img = np.clip(img, 0, 1).astype(np.float32)

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

        luma = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        luma = np.clip(luma, 0, None)
        sat = 1 + 0.3 * strength * np.sqrt(luma)
        # sat = 1 + 0.3*strength*(luma**0.5)
        img = img * sat[...,None]

        return np.clip(img,0,1)

    # ===== HISTOGRAM =====
    def draw_histogram(self, img):
        width = 350   # sau adaptezi la container
        height = 100

        hist_img = np.zeros((height, width, 3), dtype=np.uint8)

        for i, col in enumerate([(255,0,0),(0,255,0),(0,0,255)]):
            hist = cv2.calcHist([img], [i], None, [256], [0,256])
            hist = cv2.normalize(hist, hist).flatten()

            for x in range(1, width):
                idx1 = int((x-1) * 255 / width)
                idx2 = int(x * 255 / width)

                y1 = height - int(hist[idx1] * height)
                y2 = height - int(hist[idx2] * height)

                cv2.line(hist_img, (x-1, y1), (x, y2), col, 1)

        return hist_img


    def reset_image(self):
        if self.original_image is None:
            return

        # reset imagine
        self.image = self.original_image.copy()

        # ===== RESET SLIDERS =====
        self.black_slider.setValue(0)
        self.mid_slider.setValue(50)
        self.white_slider.setValue(100)
        self.enhance_slider.setValue(30)
        self.bg_slider.setValue(35)
        self.autostretch_slider.setValue(75)

        # ===== RESET CHECKBOX =====
        self.auto_wb.setChecked(True)
        self.auto_stretch.setChecked(True)
        self.stf_cb.setChecked(True)

        # update UI
        self.update_preview()
    
    # ===== LOAD =====
    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open", "", "Images (*.tif *.png *.jpg *.fits *.fit *.fts)"
        )
        if not path:
            return
        self.image_path = path

        if path.lower().endswith((".fits",".fit",".fts")):
            hdul = fits.open(path)
            data = hdul[0].data.astype(np.float32)
            hdul.close()

            if data.ndim == 3 and data.shape[0] == 3:
                data = np.transpose(data,(1,2,0))
            if data.ndim == 2:
                data = np.stack([data]*3,axis=-1)

            data -= np.nanmin(data)
            if np.nanmax(data)>0:
                data /= np.nanmax(data)

            self.image = data
        else:
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
            self.image = img

        self.original_image = self.image.copy()

        h,w = self.image.shape[:2]
        if max(h,w)<1200:
            self.preview_image = self.image.copy()
        else:
            self.preview_image = cv2.resize(self.image,(0,0),
                                            fx=self.preview_scale,
                                            fy=self.preview_scale)

        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.setFocus()

        self.update_preview()

    # ===== PROCESS =====
    def process_pipeline(self, img):
        img = img.astype(np.float32)
        if self.auto_wb.isChecked():
            img = self.auto_white_balance(img)
        img = self.stretch(img)
        img = self.apply_background(img)
        img = self.apply_enhance(img)
        return img

    # ===== PREVIEW =====
    def update_preview(self):
        if self.image is None:
            return

        img = self.preview_image
        proc = self.process_pipeline(img)

        # LEFT PANEL (original / STF)
        if self.stf_cb.isChecked():
            left_view = self.auto_stf(img)
        else:
            left_view = (img * 255).astype(np.uint8)

        # RIGHT PANEL (processed)
        right_view = (proc * 255).astype(np.uint8)

        self.display(self.original_label, left_view)
        self.display(self.processed_label, right_view)

    # ===== DISPLAY =====
    def display(self, label, img):
        if label == self.processed_label:
            h,w = img.shape[:2]
            zh = max(50,int(h/self.zoom))
            zw = max(50,int(w/self.zoom))

            x = int(self.offset_x)
            y = int(self.offset_y)

            x = max(0,min(x,w-zw))
            y = max(0,min(y,h-zh))

            img = img[y:y+zh, x:x+zw]

        rgb = img.copy()
        h,w,ch = rgb.shape
        qimg = QImage(rgb.data,w,h,ch*w,QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        pix = pix.scaled(
            label.width(),
            label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setAlignment(Qt.AlignCenter)

        label.setPixmap(pix)

    # ===== MOUSE =====
    def mouse_press(self,event):
        self.setFocus()
        if self.preview_image is None: return

        if event.modifiers() & Qt.ShiftModifier:
            self.dragging=True
            self.last_mouse_pos=event.position()
            return

        if event.button()==Qt.LeftButton:
            self.zoom*=1.25
        elif event.button()==Qt.RightButton:
            self.zoom/=1.25

        self.zoom=max(1.0,min(self.zoom,10.0))
        self.update_preview()

    def mouse_move(self,event):
        if not self.dragging: return

        pos=event.position()
        dx=pos.x()-self.last_mouse_pos.x()
        dy=pos.y()-self.last_mouse_pos.y()

        self.offset_x-=dx/self.zoom
        self.offset_y-=dy/self.zoom

        self.last_mouse_pos=pos
        self.update_preview()

    def mouse_release(self,event):
        self.dragging=False

    def mouse_double_click(self,event):
        self.zoom=1.0
        self.offset_x=0
        self.offset_y=0
        self.update_preview()

    # ===== ACTIONS =====
    def apply_changes(self):
        if self.image is not None:
            self.image = self.process_pipeline(self.image)
            self.update_preview()

 
 # ===== SAVE =====
    def save_image(self):
        if self.image is None:
            return

        # ===== DEFAULT NAME =====
        if hasattr(self, "image_path") and self.image_path:
            base_dir = os.path.dirname(self.image_path)
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            default_name = os.path.join(base_dir, base_name + "_AIST.tif")
        else:
            default_name = "output_AIST.tif"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save",
            default_name,
            "TIFF (*.tif);;PNG (*.png);;JPG (*.jpg);;FITS (*.fits)"
        )
        if not path:
            return

        img = self.process_pipeline(self.image)

        # ===== FITS =====
        if path.lower().endswith((".fit", ".fits", ".fts")):
            # flip vertical (FITS origin fix)
            img_flip = np.flipud(img)

            # RGB float32 0–1 → (3,H,W)
            rgb = np.transpose(img_flip, (2, 0, 1)).astype(np.float32)

            fits.PrimaryHDU(rgb).writeto(path, overwrite=True)
            return

        # ===== PNG / JPG / TIFF =====
        # RGB → BGR pentru OpenCV
        img_bgr_8 = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

        # JPG (doar 8-bit)
        if path.lower().endswith(".jpg"):
            cv2.imwrite(path, img_bgr_8)
            return

        # PNG (8-bit)
        if path.lower().endswith(".png"):
            cv2.imwrite(path, img_bgr_8)
            return

        # TIFF (16-bit corect)
        if path.lower().endswith(".tif"):
            img16 = (img * 65535).astype(np.uint16)
            img16 = cv2.cvtColor(img16, cv2.COLOR_RGB2BGR)
            cv2.imwrite(path, img16)
            return

    def keyPressEvent(self, event):
        if self.preview_image is None:
            return

        key = event.key()

        # ===== ZOOM =====
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom *= 1.20

        elif key == Qt.Key_Minus:
            self.zoom /= 1.25

        elif key == Qt.Key_0:
            self.zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0

        # ===== PAN (NUMPAD + ARROWS) =====
        step = 25 / self.zoom

        if key in (Qt.Key_4, Qt.Key_Left):
            self.offset_x -= step

        elif key in (Qt.Key_6, Qt.Key_Right):
            self.offset_x += step

        elif key in (Qt.Key_8, Qt.Key_Up):
            self.offset_y -= step

        elif key in (Qt.Key_2, Qt.Key_Down):
            self.offset_y += step

        # ===== LIMIT OFFSET =====
        self.clamp_offsets(self.preview_image)

        # ===== REFRESH =====
        self.zoom = max(1.0, min(self.zoom, 10.0))
        self.update_preview()

    def clamp_offsets(self, img):
        h, w = img.shape[:2]

        zh = max(50, int(h / self.zoom))
        zw = max(50, int(w / self.zoom))

        self.offset_x = max(0, min(self.offset_x, w - zw))
        self.offset_y = max(0, min(self.offset_y, h - zh))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AIMaster()
    w.show()
    sys.exit(app.exec())
