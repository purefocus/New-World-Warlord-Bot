class User:

    def __init__(self, discord_user: str, username: str, level: int, faction: str, company: str, weapons: str):
        self.discord_user = discord_user
        self.username = username
        self.level = level
        self.faction = faction
        self.company = company
        self.weapons = weapons
