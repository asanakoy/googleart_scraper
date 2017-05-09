import pandas as pd


def is_valid_artist(artist_item):
    """Check if the artist is good for us. E.g not a photographer and not a sculptor"""
    if 'bio' not in artist_item or not artist_item['bio'] or pd.isnull(artist_item['bio']):
        return True

    allowed_artist_ids = ['m01gh24', #'John Flaxman'
                         ]

    if artist_item['artist_id'] in allowed_artist_ids:
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

