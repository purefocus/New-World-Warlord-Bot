import discord
import discord.ext.commands
import discord.ui as ui
from bot_state import BotState
from dat.WarDef import WarDef


class SelectWar(ui.Select):

    def __init__(self, signup, state: BotState):

        self.signup = signup
        self.state = state

        options = []

        for w in state.wars:
            war: WarDef = state.wars[w]
            if war.active:
                loc = war.name or war.location
                options.append(discord.SelectOption(label=war.name, value=w, description=war.war_time))

        super().__init__(placeholder='Select the war to enlist in!', options=options)

    async def callback(self, interaction: discord.Interaction):
        for selected in self.values:
            war = self.state.wars[selected]
            war.add_enlistment(self.signup.as_enlistment())


class SignupButton(discord.ui.View):

    def __init__(self, state, signup):
        super().__init__()
        self.state = state
        self.signup = signup

    @discord.ui.button(label='Sign Up!', style=discord.ButtonStyle.blurple, custom_id='persistent_view:signup_btn')
    async def receive(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Please answer a few questions:',
                                                view=SelectWar(self.signup, self.state), ephemeral=True)
