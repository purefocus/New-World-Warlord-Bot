import discord


def create_embed():
    embed = discord.Embed(title='War Creation and Management')

    embed.add_field(name='War Creation',
                    inline=False,
                    value='Post the following template into __#war-boards__'
                          '```'
                          '@Warlord'

                          'Attacking Faction: <Company Name> (<Faction>) '
                          'Defending Faction: <Company Name> (<Faction>) '
                          'Contact: <Tag yourself>'
                          'War Time: <Time>'
                          'Location: <Location>'
                          'Looking for: - use ; to create a new line!'
                          '```'
                          '__*Must be ranked Consul or higher*__'''
                          ''
                          'Once the war is created, you can edit the original post to make changes as needed.'
                          ''
                          '***Note:*** Someone else can take the management role of the post by posting an __exact copy__ of the __original__ and *then* editing that post.'
                    )

    embed.add_field(name='Group Assignments',
                    inline=False,
                    value='Add the following to the end of the __original post__ from *War Creation*'
                          '```'
                          'Group 1: <Group Name>'
                          '-1: <player1> (lead, <roles>)'
                          '-2: <player2> (<roles>)'
                          '-3: <player3> (<roles>)'
                          '-4: <player4> (<roles>)'
                          '-5: <player5> (<roles>)'
                          '```'
                          'You can do it on a group-by-group basis (Don\'t need to include all 10 groups)'
                          'The players listed here do not have to be signed up as it is handled differently.'
                    )
    embed.add_field(name='Group Assignments',
                    inline=False,
                    value='To get the list of people who are signed up for a war, use the command:'
                          ' `/get_enlisted` (posts in channel) *or*'
                          '`/download_enlisted` (creates a downloadable PDF)'
                          ''
                          'Once the war has been completed, you can use the command:'
                          '`/end_war` (cannot be undone)'
                          ''
                          'To repost the war:'
                          '/repost_war'
                          ''
                          'To create a new war announcement outside of #war-boards'
                          '/post_war'
                    )

    return embed
