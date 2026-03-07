import 'package:flutter_test/flutter_test.dart';
import 'package:aura_buddy_app/main.dart';

void main() {
  testWidgets('App renders smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const AuraBuddyApp());
    expect(find.text('AURA BUDDY'), findsOneWidget);
  });
}
