from discord_ui import SlashedCommand, SelectOption, SelectMenu, SelectedMenu


async def selection(state, ctx: SlashedCommand, question, choices: list, allow_multiple=False, hidden=True):
    select_options = []

    for choice in choices:
        desc = None
        if isinstance(choice, tuple):
            choice, desc = choice
        select_options.append(SelectOption(value=choice, label=choice, description=desc))

    sel_menu = SelectMenu('selection',
                          options=select_options,
                          placeholder='Select an option',
                          max_values=len(select_options) if allow_multiple else 1)
    if hidden:
        msg = await ctx.send(question, components=[sel_menu], hidden=True)
    else:
        msg = await ctx.send(question, components=[sel_menu])

    menu: SelectedMenu = await msg.wait_for('select', state.client, timeout=state.config.question_timeout)

    await menu.respond(ninja_mode=True)
    await msg.edit(content=f'Selected: {menu.selected_values}', components=None)

    return menu.selected_values, msg
