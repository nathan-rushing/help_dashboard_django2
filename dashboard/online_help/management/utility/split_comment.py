
import re

def split_comments(comment):
    import re
    bullets = [line.strip() for line in re.split(r'[\n•]+', str(comment)) if line.strip()]
    return '<ul>' + ''.join(f'<li>{bullet}</li>' for bullet in bullets) + '</ul>' if bullets else ''


"""
def split_comments(comment):
	# Splits a comment string into a list of bullet points.
	# Handles common bullet characters and newlines.

	return [line.strip() for line in re.split(r'[\n•]+', str(comment)) if line.strip()]
	# return [line.strip() for line in re.split(r'[\n•*-]+', str(comment)) if line.strip()]
"""

