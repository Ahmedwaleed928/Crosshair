"""
Crosshair Overlay for Android (Kivy + pyjnius)
يرسم دايرة إيم في نص الشاشة فوق أي تطبيق/لعبة، والكليكات بتعدّي من خلالها.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from jnius import autoclass, cast
from android.runnable import run_on_uithread

# ===== إعدادات =====
SIZE_DP = 48          # قطر الدايرة
STROKE_DP = 2         # سمك الخط
DOT_DP = 2            # نصف قطر النقطة (0 = بدون نقطة)
COLOR = "#00FF00"     # اللون
OFFSET_X = 0          # تحريك بالبكسل
OFFSET_Y = 0
# ====================

PythonActivity = autoclass("org.kivy.android.PythonActivity")
Context = autoclass("android.content.Context")
Intent = autoclass("android.content.Intent")
Uri = autoclass("android.net.Uri")
Settings = autoclass("android.provider.Settings")
LP = autoclass("android.view.WindowManager$LayoutParams")
Gravity = autoclass("android.view.Gravity")
PixelFormat = autoclass("android.graphics.PixelFormat")
Bitmap = autoclass("android.graphics.Bitmap")
BitmapConfig = autoclass("android.graphics.Bitmap$Config")
Canvas = autoclass("android.graphics.Canvas")
Paint = autoclass("android.graphics.Paint")
PaintStyle = autoclass("android.graphics.Paint$Style")
Color = autoclass("android.graphics.Color")
ImageView = autoclass("android.widget.ImageView")


class CrosshairApp(App):
    def build(self):
        self.view = None
        self.activity = PythonActivity.mActivity
        root = BoxLayout(orientation="vertical", padding=40, spacing=20)
        self.status = Label(text="Crosshair ready", font_size="20sp")
        start = Button(text="START", font_size="24sp")
        stop = Button(text="STOP", font_size="24sp")
        start.bind(on_release=lambda *_: self.start())
        stop.bind(on_release=lambda *_: self.stop())
        for w in (self.status, start, stop):
            root.add_widget(w)
        return root

    # ---------- permission ----------
    def can_draw(self):
        return Settings.canDrawOverlays(self.activity)

    def ask_permission(self):
        uri = Uri.parse("package:" + self.activity.getPackageName())
        intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, uri)
        self.activity.startActivity(intent)

    # ---------- actions ----------
    def start(self):
        if not self.can_draw():
            self.status.text = "Allow 'Display over other apps', then press START again"
            self.ask_permission()
            return
        if self.view is not None:
            self.status.text = "Already running"
            return
        self.status.text = "Crosshair ON"
        self._show()

    def stop(self):
        self.status.text = "Crosshair OFF"
        self._hide()

    # ---------- overlay (UI thread) ----------
    @run_on_uithread
    def _show(self):
        if self.view is not None:
            return
        act = self.activity
        density = act.getResources().getDisplayMetrics().density
        size = int(SIZE_DP * density)
        stroke = max(1, int(STROKE_DP * density))
        pad = stroke * 2
        full = size + pad * 2
        c = full / 2.0

        bmp = Bitmap.createBitmap(full, full, BitmapConfig.ARGB_8888)
        canvas = Canvas(bmp)
        paint = Paint(1)  # ANTI_ALIAS_FLAG
        paint.setColor(Color.parseColor(COLOR))
        paint.setStyle(PaintStyle.STROKE)
        paint.setStrokeWidth(float(stroke))
        canvas.drawCircle(c, c, size / 2.0, paint)
        if DOT_DP > 0:
            paint.setStyle(PaintStyle.FILL)
            canvas.drawCircle(c, c, float(DOT_DP * density), paint)

        iv = ImageView(act)
        iv.setImageBitmap(bmp)

        flags = (
            LP.FLAG_NOT_FOCUSABLE
            | LP.FLAG_NOT_TOUCHABLE
            | LP.FLAG_NOT_TOUCH_MODAL
            | LP.FLAG_LAYOUT_IN_SCREEN
        )
        params = LP(full, full, LP.TYPE_APPLICATION_OVERLAY, flags,
                    PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.CENTER
        params.x = OFFSET_X
        params.y = OFFSET_Y

        wm = cast("android.view.WindowManager",
                  act.getSystemService(Context.WINDOW_SERVICE))
        wm.addView(iv, params)
        self.view = iv

    @run_on_uithread
    def _hide(self):
        if self.view is None:
            return
        wm = cast("android.view.WindowManager",
                  self.activity.getSystemService(Context.WINDOW_SERVICE))
        wm.removeView(self.view)
        self.view = None

    def on_stop(self):
        self._hide()


if __name__ == "__main__":
    CrosshairApp().run()
