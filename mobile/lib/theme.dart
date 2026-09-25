import 'package:flutter/material.dart';

/// Paper in light, near-black in dark. Gold focus. No analytics.
const Color kMatteBlack = Color(0xFF0B0B0B);
const Color kSurface = Color(0xFF141414);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF8A7219);
const Color kIvory = Color(0xFFE8E0D0);
const Color kPaper = Color(0xFFF4F0E6);
const Color kInk = Color(0xFF1A1714);

ThemeData buildAppTheme({Brightness brightness = Brightness.dark}) {
  final dark = brightness == Brightness.dark;
  final scheme = dark
      ? const ColorScheme.dark(
          primary: kGold,
          onPrimary: kMatteBlack,
          secondary: kGoldDim,
          onSecondary: kIvory,
          surface: kSurface,
          onSurface: kIvory,
          error: Color(0xFFB54A4A),
          onError: kIvory,
        )
      : const ColorScheme.light(
          primary: Color(0xFF7D6410),
          onPrimary: kPaper,
          secondary: kGoldDim,
          onSecondary: kInk,
          surface: Colors.white,
          onSurface: kInk,
          error: Color(0xFFB54A4A),
          onError: Colors.white,
        );
  return ThemeData(
    useMaterial3: true,
    brightness: brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: dark ? kMatteBlack : kPaper,
    appBarTheme: AppBarTheme(
      backgroundColor: dark ? kMatteBlack : kPaper,
      foregroundColor: dark ? kGold : kInk,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: dark ? kSurface : Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0x33C9A227)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: dark ? const Color(0xFF1A1A1A) : Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: scheme.primary, width: 2),
      ),
    ),
    segmentedButtonTheme: SegmentedButtonThemeData(
      style: ButtonStyle(
        foregroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kMatteBlack : kIvory;
        }),
        backgroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kGold : kSurface;
        }),
      ),
    ),
  );
}
