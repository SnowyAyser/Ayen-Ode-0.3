import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

/// HSL rose-curve loader, ported from `static/clover-loader.js`.
///
/// The web version pre-computes a 600-point unit rose curve `r = cos(2θ)` and
/// draws a trail with HSL interpolation along the head's recency. We do the
/// same with a [CustomPainter] driven by a [Ticker].
///
/// Pass a `hue` in degrees:
///   * 38 → amber (used everywhere except login)
///   * 142 → emerald (used as the default elsewhere)
///   * the login canvas paints its own bespoke RGB green — for that, use
///     [CloverLoader.rgb].
class CloverLoader extends StatefulWidget {
  const CloverLoader({
    super.key,
    this.size = 48,
    this.hue = 142,
  }) : rgb = null;

  const CloverLoader.rgb({
    super.key,
    this.size = 48,
    required Color this.rgb,
  }) : hue = 0;

  final double size;
  final int hue;
  final Color? rgb;

  @override
  State<CloverLoader> createState() => _CloverLoaderState();
}

class _CloverLoaderState extends State<CloverLoader>
    with SingleTickerProviderStateMixin {
  late final Ticker _ticker;
  double _pos = 0;

  @override
  void initState() {
    super.initState();
    _ticker = createTicker((_) {
      // Mirrors the web's `pos = (pos + 2.5) % TOTAL` step.
      setState(() => _pos = (_pos + 2.5) % _CloverPainter.total);
    })
      ..start();
  }

  @override
  void dispose() {
    _ticker.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(widget.size, widget.size),
      painter: _CloverPainter(
        pos: _pos,
        hue: widget.hue,
        rgb: widget.rgb,
      ),
    );
  }
}

class _CloverPainter extends CustomPainter {
  _CloverPainter({required this.pos, required this.hue, this.rgb});

  static const int total = 600;
  // 80% of total — see clover-loader.js TRAIL_MAX.
  static const int trailMax = 480;
  static const double fadeFrac = 0.65;

  final double pos;
  final int hue;
  final Color? rgb;

  // Pre-computed unit rose curve.
  static final List<Offset> _unit = List.generate(total, (i) {
    final t = (i / total) * math.pi * 2;
    final r = math.cos(2 * t);
    return Offset(r * math.cos(t), r * math.sin(t));
  });

  @override
  void paint(Canvas canvas, Size size) {
    final px = size.width;
    final scale = px * 0.42;
    final cx = px / 2;
    final cy = px / 2;
    final lineW = math.max(1.5, px * 0.022);
    final dotR = math.max(2.0, px * 0.046);
    final glowR = dotR * 3.5;

    final head = pos.floor() % total;
    final trailLen = trailMax;
    final solidLen = (trailLen * fadeFrac).toInt();

    for (int age = trailLen; age >= 1; age--) {
      final a = (head - age + total * 8) % total;
      final b = (a + 1) % total;
      double alpha;
      if (age <= solidLen) {
        alpha = 1.0;
      } else {
        final denom = (trailLen - solidLen).toDouble();
        alpha = 1.0 - (age - solidLen) / (denom == 0 ? 1 : denom);
      }
      if (alpha < 0.01) continue;

      final recency = 1.0 - age / trailMax;
      final color = _strokeColor(recency, alpha);

      final paint = Paint()
        ..color = color
        ..strokeWidth = lineW
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      canvas.drawLine(
        Offset(cx + _unit[a].dx * scale, cy + _unit[a].dy * scale),
        Offset(cx + _unit[b].dx * scale, cy + _unit[b].dy * scale),
        paint,
      );
    }

    // Glowing head dot.
    final hx = cx + _unit[head].dx * scale;
    final hy = cy + _unit[head].dy * scale;
    final glowPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          _hsla(hue - 10, 100, 88, 0.55),
          _hsla(hue, 70, 65, 0.22),
          _hsla(hue, 70, 60, 0),
        ],
        stops: const [0, 0.4, 1],
      ).createShader(Rect.fromCircle(center: Offset(hx, hy), radius: glowR));
    canvas.drawCircle(Offset(hx, hy), glowR, glowPaint);

    final headPaint = Paint()..color = _hsla(hue - 5, 80, 90, 1);
    canvas.drawCircle(Offset(hx, hy), dotR, headPaint);
  }

  Color _strokeColor(double recency, double alpha) {
    if (rgb != null) return rgb!.withValues(alpha: alpha);
    final lightness = 22 + recency * 42;
    final sat = 55 + recency * 30;
    return _hsla(hue, sat, lightness, alpha);
  }

  Color _hsla(num hDeg, num sPct, num lPct, double alpha) {
    final h = (hDeg % 360 + 360) % 360 / 360.0;
    final s = (sPct / 100).clamp(0.0, 1.0).toDouble();
    final l = (lPct / 100).clamp(0.0, 1.0).toDouble();
    final c = (1 - (2 * l - 1).abs()) * s;
    final x = c * (1 - (((h * 6) % 2) - 1).abs());
    final m = l - c / 2;
    double r, g, b;
    final hp = h * 6;
    if (hp < 1) {
      r = c; g = x; b = 0;
    } else if (hp < 2) {
      r = x; g = c; b = 0;
    } else if (hp < 3) {
      r = 0; g = c; b = x;
    } else if (hp < 4) {
      r = 0; g = x; b = c;
    } else if (hp < 5) {
      r = x; g = 0; b = c;
    } else {
      r = c; g = 0; b = x;
    }
    return Color.fromRGBO(
      ((r + m) * 255).round(),
      ((g + m) * 255).round(),
      ((b + m) * 255).round(),
      alpha,
    );
  }

  @override
  bool shouldRepaint(covariant _CloverPainter old) =>
      old.pos != pos || old.hue != hue || old.rgb != rgb;
}
