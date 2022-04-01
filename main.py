from dc.bot import background_loop, bot, dc_cfg


def main():
    background_loop.start()
    bot.run(dc_cfg.token)


if __name__ == "__main__":
    main()
