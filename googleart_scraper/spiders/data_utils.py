import pandas as pd


def is_valid_artist(artist_item):
    """Check if the artist is good for us. E.g not a photographer and not a sculptor"""
    allowed_artist_ids = ['m01gh24',  # 'John Flaxman'
                          ]
    disallowed_artist_ids = ['m0f2cl4',  # glass artist
                             't218rckd4dh',  # berenice-abbott - photographer
                             'm02hs4v',  # berenice-abbott - photographer
                             'm023gfm',  # photographer worked with Turkish painter
                             't2194x6_5fg',  # photographer worked with Turkish painter
                             'm011srtqs',  # street sculptures
                             't218rckdgl4',  # street sculptures
                             't2194x6qhjg',
                             't218rckd8n9',
                             'm0t50cxp',
                             'm0t5fk6y',
                             'm0t50531',
                             'm0t50bqk',
                             'm0t509bm',
                             'm0t5fw1y',
                             'm0t505rk',
                             'm0vs9w6q',
                             'm0t50fjq',
                             'm0t5fpmx',
                             'm0vnnqm0'
                             ]
    if artist_item['artist_id'] in allowed_artist_ids:
        return True
    if artist_item['artist_id'] in disallowed_artist_ids:
        return False

    if 'bio' not in artist_item or not artist_item['bio'] or pd.isnull(artist_item['bio']):
        return True

    negative_keywords = ['photographer', 'photojournalist', 'sculptor', 'world press photo']
    positive_keywords = ['illustrator', 'painter']

    for key in positive_keywords:
        if key in artist_item['bio'].lower():
            return True

    for key in negative_keywords:
        if key in artist_item['bio'].lower():
            return False

    return True
