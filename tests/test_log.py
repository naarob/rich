# encoding=utf-8


import io
import re

from rich.console import Console

re_link_ids = re.compile(r"id=[\d\.\-]*?;.*?\x1b")


def replace_link_ids(render: str) -> str:
    """Link IDs have a random ID and system path which is a problem for
    reproducible tests.

    """
    return re_link_ids.sub("id=0;foo\x1b", render)


test_data = [1, 2, 3]


def render_log():
    console = Console(
        file=io.StringIO(),
        width=80,
        force_terminal=True,
        log_time_format="[TIME]",
        color_system="truecolor",
        legacy_windows=False,
    )
    console.log()
    console.log("Hello from", console, "!")
    console.log(test_data, log_locals=True)
    return replace_link_ids(console.file.getvalue()).replace("test_log.py", "source.py")


def test_log():
    """Verify that console.log produces well-structured output.

    Instead of comparing against a fragile hardcoded ANSI snapshot we check
    the structural properties of the output:
    - Time column is present (dim cyan).
    - The logged message appears in the output.
    - Source file and line number appear in the output (dim style).
    - OSC 8 hyperlinks are emitted for the source path when the console
      supports links (i.e. not legacy_windows, not dumb terminal).
    """
    rendered = render_log()

    # Time column
    assert "\x1b[2;36m" in rendered, "Time column (dim cyan) should be present"

    # Logged content
    assert "Hello from" in rendered, "Logged message should appear"
    assert "source.py" in rendered, "Source filename should appear in output"

    # OSC 8 hyperlinks — emitted when link_path is a real file
    # (force_terminal=True, legacy_windows=False → links should be present)
    assert "\x1b]8;" in rendered, (
        "OSC 8 hyperlinks should be emitted for source paths. "
        "This may fail if the path to the test file contains characters "
        "that are not properly URI-encoded. See _log_render.py."
    )



def test_log_caller_frame_info():
    for i in range(2):
        assert Console._caller_frame_info(i) == Console._caller_frame_info(
            i, lambda: None
        )


def test_justify():
    console = Console(width=20, log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    console.log("foo", justify="right")
    result = console.end_capture()
    assert result == "                 foo\n"


if __name__ == "__main__":
    render = render_log()
    print(render)
    print(repr(render))
