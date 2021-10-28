import discord


def create_embed():
    embed = discord.Embed(title='War Creation and Management', colour=discord.Colour(0x470000),
                          description='This post will explain how to create and manage wars using the Warlord Bot!')

    embed.add_field(name='War Creation',
                    inline=False,
                    value='Post the following template into __#war-boards__\n'
                          '```\n'
                          '@Warlord\n'
                          '\n'
                          'Attacking Faction: <Company Name> (<Faction>) \n'
                          'Defending Faction: <Company Name> (<Faction>) \n'
                          'Contact: <Tag yourself>\n'
                          'War Time: <Time>\n'
                          'Location: <Location>\n'
                          'Looking for: use ; to create a new line!\n'
                          '\n'
                          '---\n'
                          'Any additional information you want to post goes here!\n'
                          'Can be no more than 1024 characters!\n'
                          '---\n'
                          '```\n'
                          '__*Must be ranked Consul or higher*__\n'
                          '\n'
                          'Once the war is created, you can edit the original post to make changes as needed.\n'
                          '\n'
                          '***Note:*** Someone else can take the management role of the post by posting an __exact copy__ of the __original__ and *then* editing that post.\n'
                    )

    embed.add_field(name='Group Assignments',
                    inline=False,
                    value='Add the following to the end of the __original post__ from *War Creation*\n'
                          '```\n'
                          'Group 1: <Group Name>\n'
                          '-1: <player1> (lead, <roles>)\n'
                          '-2: <player2> (<roles>)\n'
                          '-3: <player3> (<roles>)\n'
                          '-4: <player4> (<roles>)\n'
                          '-5: <player5> (<roles>)\n'
                          '```\n'
                          'You can do it on a group-by-group basis (Don\'t need to include all 10 groups)\n'
                          'The players listed here do not have to be signed up as it is handled differently.\n'
                    )
    embed.add_field(name='Group Assignments',
                    inline=False,
                    value='To get the list of people who are signed up for a war, use the command:\n'
                          ' `/get_enlisted` (posts in channel) *or*\n'
                          '`/download_enlisted` (creates a downloadable PDF)\n'
                          '\n'
                          'Once the war has been completed, you can use the command:\n'
                          '`/end_war` (cannot be undone)\n'
                          '\n'
                          'To repost the war:\n'
                          '`/repost_war`\n'
                          '\n'
                          'To create a new war announcement outside of #war-boards\n'
                          '`/post_war`\n'
                    )

    embed.add_field(name='Feedback',
                    inline=False,
                    value='I am always looking for feedback on the Warlord bot!\n'
                          'If you have any suggestions and feature requests, please @purefocus#3061 know!\n'
                          'Also report any bugs you find as well! (enlistment issues, war creation issues, etc..)'
                    )

    return embed
