from app.game import Game


def main():
    game = Game(mode="continue", scale=4)
    game.run()


if __name__ == "__main__":
    main()
