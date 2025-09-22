def make_trace(script_path):
    def trace_function(frame, event, arg):
        if event == 'line' and frame.f_code.co_filename == script_path:
            local_vars = {k: v for k, v in frame.f_locals.items() if not k.startswith('_') and not callable(v)}
            print(f"Line {frame.f_lineno}: {local_vars}")
        return trace_function

    return trace_function


def run_script(script_path):
    with open(script_path) as f:
        code = compile(f.read(), script_path, 'exec')
        exec(code, {'__name__': '__main__'})


if __name__ == "__main__":
    import sys

    script_path = sys.argv[1]
    sys.settrace(make_trace(script_path))
    run_script(script_path)
