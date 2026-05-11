import 'package:freezed_annotation/freezed_annotation.dart';

part 'game_time.freezed.dart';
part 'game_time.g.dart';

@freezed
class GameTime with _$GameTime {
  const factory GameTime({
    @Default(0) int seconds,
    String? label,
  }) = _GameTime;

  factory GameTime.fromJson(Map<String, dynamic> json) =>
      _$GameTimeFromJson(json);
}
