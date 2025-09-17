ACTIVE_BORDER_COLOR = "red"
ACTIVE_BORDER_WIDTH = 4
ACTIVE_STYLE = "solid"


def node_to_dot(_id, shape, label, style, fillcolor, border_color=None, border_size=None):
    other_code = ""
    if border_color is not None:
        other_code += f'color={border_color} '
    if border_size is not None:
        other_code += f'penwidth={border_size} '
    return f'\nnode_{_id}[shape={shape} label="{label or ""}" style="{style or ""}" fillcolor={fillcolor} {other_code or ""}];'


def gateway_to_dot(_id, label, style, fillcolor, border_color=None, border_size=None):
    return node_to_dot(_id, "diamond", label, style, fillcolor, border_color, border_size)


def exclusive_gateway_to_dot(_id, label, style, border_color=None, border_size=None):
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    return gateway_to_dot(_id, label, style, "orange", border_color, border_size)


def parallel_gateway_to_dot(_id, style, border_color=None, border_size=None):
    return gateway_to_dot(_id, f"+", style, "green", border_color, border_size)


def probabilistic_gateway_to_dot(_id, name, style, border_color=None, border_size=None):
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    return gateway_to_dot(_id, f"{name}", style, "yellowgreen", border_color, border_size)


def loop_gateway_to_dot(_id, label, style, border_color=None, border_size=None):
    if style is None:
        style = "filled"
    else:
        style = f"filled,{style}"
    return gateway_to_dot(_id, label, style, "yellowgreen", border_color, border_size)


def task_to_dot(_id, name, style, impacts, duration, impacts_names, border_color=None, border_size=None):
    additional_label = ""
    if impacts:
        tmp = ", ".join(f"\\n{key}: {value}" for key, value in zip(impacts_names, impacts))
        additional_label += f"\\n impacts: {tmp}"
    if duration:
        additional_label += f"\\n duration: {duration}"

    if style is None:
        style = "rounded,filled"
    else:
        style = f"rounded,filled,{style}"

    return node_to_dot(
        _id,
        "rectangle",
        f"{name}{additional_label}",
        style,
        "lightblue",
        border_color,
        border_size
    )


def arc_to_dot(from_id, to_id, label=None):
    if label is None:
        return f'\nnode_{from_id} -> node_{to_id};\n'
    else:
        return f'\nnode_{from_id} -> node_{to_id}[label="{label}"];\n'


def wrap_to_dot(region_root: dict, impacts_names: list[str], active_regions: set[str] = None):
    """
    Wrapper to create the dot representation of the BPMN.
    :param region_root: Parse tree of the expression
    :param impacts_names: Impacts names to display
    :param active_regions: Ids of the active regions to highlight
    :return: Dot representation of the BPMN
    """

    if active_regions is None:
        active_regions = set()

    code = "digraph G {\n"
    code += "rankdir=LR;\n"
    code += 'start[label="" style="filled" shape=circle fillcolor=palegreen1]\n'
    code += 'end[label="" style="filled" shape=doublecircle fillcolor=orangered] \n'
    other_code, entry_id, exit_id = region_to_dot(region_root, impacts_names, active_regions)
    code += other_code
    code += f'start -> node_{entry_id};\n'
    code += f'node_{exit_id} -> end;\n'
    code += "\n}"

    return code


def serial_generator():
    """Generator to create unique IDs."""
    id_counter = 0
    while True:
        yield id_counter
        id_counter += 1


id_generator = serial_generator()


def region_to_dot(region_root, impacts_names, active_regions):
    is_active = region_root.get('id') in active_regions
    if region_root.get("type") == 'task':
        _id = next(id_generator)
        return task_to_dot(
            _id,
            region_root.get('label'),
            ACTIVE_STYLE if is_active else None,
            region_root.get('impacts', []),
            region_root.get('duration'),
            impacts_names,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        ), _id, _id
    elif region_root.get("type") == 'loop':
        entry_id = next(id_generator)
        ext_id = next(id_generator)

        # Entry point
        code = loop_gateway_to_dot(
            entry_id,
            region_root.get('label'),
            style=None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += loop_gateway_to_dot(
            ext_id,
            region_root.get('label'),
            region_root.get('style')
        )

        # Child
        other_code, child_entry_id, child_exit_id = region_to_dot(region_root.get('children')[0], impacts_names,
                                                                  active_regions)
        code += other_code
        p = region_root.get('distribution')
        code += arc_to_dot(entry_id, child_entry_id, p)
        code += arc_to_dot(child_exit_id, ext_id, 1 - p)

        return code, entry_id, ext_id
    elif region_root.get("type") == 'choice':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = exclusive_gateway_to_dot(
            entry_id,
            region_root.get('label'),
            ACTIVE_STYLE if is_active else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += exclusive_gateway_to_dot(
            last_exit_id,
            region_root.get('label'),
            style=None
        )

        # Children
        for child in region_root.get('children', []):
            child_code, child_entry_id, child_exit_id = region_to_dot(child, impacts_names, active_regions)
            code += child_code
            code += arc_to_dot(entry_id, child_entry_id)
            code += arc_to_dot(child_exit_id, last_exit_id)

        return code, entry_id, last_exit_id
    elif region_root.get("type") == 'parallel':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = parallel_gateway_to_dot(
            entry_id,
            style=ACTIVE_STYLE if is_active else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += parallel_gateway_to_dot(
            last_exit_id,
            style=None
        )

        # Children
        for child in region_root.get('children', []):
            child_code, child_entry_id, child_exit_id = region_to_dot(child, impacts_names, active_regions)
            code += child_code
            code += arc_to_dot(entry_id, child_entry_id)
            code += arc_to_dot(child_exit_id, last_exit_id)

        return code, entry_id, last_exit_id
    elif region_root.get("type") == 'nature':
        entry_id = next(id_generator)
        last_exit_id = next(id_generator)

        # Entry point
        code = probabilistic_gateway_to_dot(
            entry_id,
            region_root.get('label'),
            style=ACTIVE_STYLE if is_active else None,
            border_color=ACTIVE_BORDER_COLOR if is_active else None,
            border_size=ACTIVE_BORDER_WIDTH if is_active else None
        )

        # Exit point
        code += probabilistic_gateway_to_dot(
            last_exit_id,
            region_root.get('label'),
            style=None
        )

        # Children
        for child, p in zip(region_root.get('children', []), region_root.get("distribution", [])):
            child_code, child_entry_id, child_exit_id = region_to_dot(child, impacts_names, active_regions)
            code += child_code
            code += arc_to_dot(entry_id, child_entry_id, p)
            code += arc_to_dot(child_exit_id, last_exit_id)

        return code, entry_id, last_exit_id
    elif region_root.get("type") == 'sequential':
        code = ""
        entry_id = None
        last_exit_id = None

        for i, child in enumerate(region_root.get('children', [])):
            child_code, child_entry_id, child_exit_id = region_to_dot(child, impacts_names, active_regions)
            code += child_code

            arc = arc_to_dot(last_exit_id, child_entry_id) if last_exit_id is not None else ""
            if entry_id is None:
                entry_id = child_entry_id
                arc = ""

            last_exit_id = child_exit_id
            code += arc

        return code, entry_id, last_exit_id
    else:
        raise ValueError(f"Unknown type: {region_root['type']}")


def get_active_region_by_pn(petri_net, marking):
    active_regions = set()

    for place in petri_net.get("places", []):
        place_id = place["id"]
        entry_region_id = place.get("entry_region_id")
        place_state = marking.get(place_id, {"token": 0})
        if entry_region_id and place_state['token'] > 0:
            active_regions.add(entry_region_id)

    return active_regions
