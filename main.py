import pygame
import sys
import os

# 画面設定
WIDTH, HEIGHT = 800, 600
BG_COLOR = (40, 40, 40)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 0)
AXIS_COLOR = (200, 200, 200)

def main():
    # Pygameとジョイスティックの初期化
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    pygame.init()
    pygame.joystick.init()

    # 画面の初期化
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pro Controller Tester")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("menlo", 24)

    # コントローラーの数を取得
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("⚠️ エラー: コントローラーが見つかりません。")
        pygame.quit()
        sys.exit()

    # 最初のコントローラーを取得
    joystick = pygame.joystick.Joystick(0)
    # pygame-ce 2.4以降ではJoystick.init()は非推奨で不要になったため削除
    
    # ボタンのマッピング (Nintendo Switch Pro Controller)
    # 接続環境やOSによってマッピングが異なる場合があります。
    button_names = {
        0: "B", 1: "A", 2: "Y", 3: "X", 
        4: "L", 5: "R", 6: "ZL", 7: "ZR",
        8: "-", 9: "+", 10: "L3 (Left Stick Click)", 11: "R3 (Right Stick Click)",
        12: "Home", 13: "Capture", 
        14: "D-Pad Up", 15: "D-Pad Down", 16: "D-Pad Left", 17: "D-Pad Right",
        18: "Misc1", 19: "Misc2"
    }

    # ジョイスティックの軸とデッドゾーン
    axes = [0.0] * joystick.get_numaxes()
    # MacOS等、SDLのバージョンや環境によって `get_button` と `JOYBUTTONDOWN` イベントが
    # 正しく発火しない場合があるため、毎フレーム `get_button(i)` で直接状態をポーリングします。
    buttons = [False] * joystick.get_numbuttons()
    hat = (0, 0)

    try:
        while True:
            # イベント処理（終了対応と軸の取得）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis < len(axes):
                        # デッドゾーン適用
                        val = event.value if abs(event.value) > 0.1 else 0.0
                        axes[event.axis] = val
                elif event.type == pygame.JOYHATMOTION:
                    hat = event.value

            # === ボタンの状態を毎フレーム直接取得 (ポーリング) ===
            for i in range(joystick.get_numbuttons()):
                buttons[i] = joystick.get_button(i)

            # 画面の描画
            screen.fill(BG_COLOR)

            # タイトル
            title_text = font.render(f"Controller: {joystick.get_name()}", True, HIGHLIGHT_COLOR)
            screen.blit(title_text, (20, 20))

            # ボタンの状態を表示（2列に分割して表示）
            y_offset = 60
            for i, state in enumerate(buttons):
                name = button_names.get(i, f"Btn {i}")
                color = HIGHLIGHT_COLOR if state else TEXT_COLOR
                text = font.render(f"{i:02d}: {name} [{ 'ON' if state else 'OFF' }]", True, color)
                # 左列（0〜9）、右列（10〜19）に配置
                x_pos = 20 if i < 10 else 240
                y_pos = y_offset + (i % 10) * 25
                screen.blit(text, (x_pos, y_pos))

            # 十字キー (Hat) の状態を表示
            # （MacのProコントローラー接続ではHatが0個として認識され、ボタンとして割り当てられることが多いですが、念のため表示は残します）
            hat_text = font.render(f"Hat Status: {hat}", True, HIGHLIGHT_COLOR if hat != (0, 0) else TEXT_COLOR)
            screen.blit(hat_text, (20, 350))

            # スティックのグラフィカル表示 (左スティック: 軸0, 1)
            left_stick_x = 550
            left_stick_y = 200
            pygame.draw.circle(screen, AXIS_COLOR, (left_stick_x, left_stick_y), 50, 2)
            if len(axes) >= 2:
                Lx = int(left_stick_x + axes[0] * 50)
                Ly = int(left_stick_y + axes[1] * 50)
                pygame.draw.circle(screen, HIGHLIGHT_COLOR, (Lx, Ly), 10)
                screen.blit(font.render("L-Stick", True, TEXT_COLOR), (left_stick_x - 40, left_stick_y - 80))
                screen.blit(font.render(f"X: {axes[0]:.2f}", True, TEXT_COLOR), (left_stick_x - 40, left_stick_y + 60))
                screen.blit(font.render(f"Y: {axes[1]:.2f}", True, TEXT_COLOR), (left_stick_x - 40, left_stick_y + 80))

            # スティックのグラフィカル表示 (右スティック: 軸2, 3)
            right_stick_x = 620
            right_stick_y = 200
            pygame.draw.circle(screen, AXIS_COLOR, (right_stick_x, right_stick_y), 50, 2)
            if len(axes) >= 4:
                Rx = int(right_stick_x + axes[2] * 50)
                Ry = int(right_stick_y + axes[3] * 50)
                pygame.draw.circle(screen, HIGHLIGHT_COLOR, (Rx, Ry), 10)
                screen.blit(font.render("R-Stick", True, TEXT_COLOR), (right_stick_x - 40, right_stick_y - 80))
                screen.blit(font.render(f"X: {axes[2]:.2f}", True, TEXT_COLOR), (right_stick_x - 40, right_stick_y + 60))
                screen.blit(font.render(f"Y: {axes[3]:.2f}", True, TEXT_COLOR), (right_stick_x - 40, right_stick_y + 80))

            # トリガー (軸4, 5 がある場合)
            if len(axes) >= 6:
                screen.blit(font.render("Triggers", True, TEXT_COLOR), (420, 350))
                
                # 左トリガー
                pygame.draw.rect(screen, AXIS_COLOR, (420, 390, 25, 100), 2)
                # トリガーは -1.0(未入力) ～ 1.0(最大) の範囲であることが多いため、0.0〜1.0に正規化
                l_trig = max(0, (axes[4] + 1) / 2) if axes[4] != 0 else 0
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (420, 390 + 100 * (1 - l_trig), 25, 100 * l_trig))
                screen.blit(font.render("ZL (Axis 4)", True, TEXT_COLOR), (420, 500))

                # 右トリガー
                pygame.draw.rect(screen, AXIS_COLOR, (620, 390, 25, 100), 2)
                r_trig = max(0, (axes[5] + 1) / 2) if axes[5] != 0 else 0
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (620, 390 + 100 * (1 - r_trig), 25, 100 * r_trig))
                screen.blit(font.render("ZR (Axis 5)", True, TEXT_COLOR), (620, 500))

            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
