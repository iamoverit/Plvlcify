from dataclasses import dataclass
import io
import os
import unicodedata


@dataclass
class m3u:
    name: str
    path: str


def is_music(path):
    support_extension = ['.mp3', '.m3u', '.wma', '.flac',
                         '.wav', '.mc', '.aac', '.m4a',
                         '.ape', '.dsf', '.dff']
    _, extension = os.path.splitext(path)
    if extension.lower() in support_extension:
        return True
    return False


def create_playList(select_dir, request):
    m3u_list = []
    for root, _, files in os.walk((select_dir / 'music')):
        for filename in files:
            rel_dir = os.path.relpath(root, select_dir)
            if rel_dir == ".":
                path = filename
            else:
                path = os.path.join(rel_dir, filename)
            if is_music(path):
                url_for_path = request.app.router['static'].url_for(
                    filename=path)
                m3u_list.append(
                    m3u(filename, str(request.clone(rel_url=url_for_path).url)))
    # m3u_list.sort()
    return m3u_list
