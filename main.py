import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

SIZE_DP = 48
STROKE_DP = 2
DOT_DP = 2
COLOR = "#00FF00"
OFFSET_X = 0
OFFSET_Y = 0


class CrosshairApp(App):
    def build(self):
        self.view = None
        root = BoxLayout(orientation="vertical", padding=30, spacing=20)
        self.status = Label(text="Crosshair ready", font_size="14sp",
                            halign="left", valign="middle")
        self.status.bind(size=lambda w, s: setattr(w, "text_size", s))
        start = Button(text="START", font_size="24sp")
        stop = Button(text="STOP", font_size="24sp")
        start.bind(on_release=lambda *_: self.start())
        stop.bind(on_release=lambda *_: self.stop())
        for w in (self.status, start, stop):
            root.add_widget(w)
        return root

    def set_status(self, text):
        self.status.text = text

    def report(self):
        self.set_status(traceback.format_exc()[-900:])

    def start(self):
        try:
            from jnius import autoclass
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            Settings = autoclass("android.provider.Settings")
            if not Settings.canDrawOverlays(activity):
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                uri = Uri.parse("package:" + activity.getPackageName())
                activity.startActivity(
                    Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, uri))
                self.set_status("Allow overlay permission, then press START again")
                return
            if self.view is not None:
                self.set_status("Already running")
                return
            self._show()
        except Exception:
            self.report()

    def stop(self):
        try:
            self._hide()
            self.set_status("Crosshair OFF")
        except Exception:
            self.report()

    def _show(self):
        from android.runnable import run_on_uithread

        @run_on_uithread
        def job():
            try:
                from jnius import autoclass, cast
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                Context = autoclass("android.content.Context")
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

                density = activity.getResources().getDisplayMetrics().density
                size = int(SIZE_DP * density)
                stroke = max(1, int(STROKE_DP * density))
                full = size + stroke * 4
                c = full / 2.0

                bmp = Bitmap.createBitmap(full, full, BitmapConfig.ARGB_8888)
                canvas = Canvas(bmp)
                paint = Paint(1)
                paint.setColor(Color.parseColor(COLOR))
                paint.setStyle(PaintStyle.STROKE)
                paint.setStrokeWidth(float(stroke))
                canvas.drawCircle(c, c, size / 2.0, paint)
                if DOT_DP > 0:
                    paint.setStyle(PaintStyle.FILL)
                    canvas.drawCircle(c, c, float(DOT_DP * density), paint)

                iv = ImageView(activity)
                iv.setImageBitmap(bmp)

                flags = (LP.FLAG_NOT_FOCUSABLE | LP.FLAG_NOT_TOUCHABLE
                         | LP.FLAG_NOT_TOUCH_MODAL | LP.FLAG_LAYOUT_IN_SCREEN)
                params = LP(full, full, LP.TYPE_APPLICATION_OVERLAY, flags,
                            PixelFormat.TRANSLUCENT)
                params.gravity = Gravity.CENTER
                params.x = OFFSET_X
                params.y = OFFSET_Y

                wm = cast("android.view.WindowManager",
                          activity.getSystemService(Context.WINDOW_SERVICE))
                wm.addView(iv, params)
                self.view = iv
                Clock.schedule_once(lambda dt: self.set_status("Crosshair ON"))
            except Exception:
                err = traceback.format_exc()[-900:]
                Clock.schedule_once(lambda dt: self.set_status(err))

        job()

    def _hide(self):
        if self.view is None:
            return
        from android.runnable import run_on_uithread
        view = self.view
        self.view = None

        @run_on_uithread
        def job():
            try:
                from jnius import autoclass, cast
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                Context = autoclass("android.content.Context")
                wm = cast("android.view.WindowManager",
                          activity.getSystemService(Context.WINDOW_SERVICE))
                wm.removeView(view)
            except Exception:
                pass

        job()

    def on_stop(self):
        try:
            self._hide()
        except Exception:
            pass


if __name__ == "__main__":
    CrosshairApp().run()
