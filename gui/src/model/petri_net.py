def get_targets(petri_net, component_id):
    """
    Given a Petri net and a component ID, return the target transitions or places
    """
    component = None
    for place in petri_net['places']:
        if place['id'] == component_id:
            component = place
            break
    if not component:
        for transition in petri_net['transitions']:
            if transition['id'] == component_id:
                component = transition
                break
    if not component:
        return []

    return [arc['target'] for arc in petri_net['arcs'] if arc['source'] == component_id]


def get_choices_for_exclusive_gateway(petri_net, place_id):
    """
    Given a Petri net and a place ID, return the possible choices (transitions)
    """
    region_transitions = {}

    place_targets = get_targets(petri_net, place_id)
    for transition in place_targets:
        transition_targets = get_targets(petri_net, transition)
        transition_info = get_transition_info(petri_net, transition)
        if len(transition_targets) > 1:
            # TODO: log warning
            pass
        choice_place = get_place_info(petri_net, transition_targets[0])
        region_transitions[choice_place['label']] = dict(label=choice_place['entry_region_id'],
                                                         transition_id=transition,
                                                         probability=transition_info.get('probability', 0.5))

    return region_transitions


def get_place_info(petri_net, place_id):
    """
    Given a Petri net and a place ID, return the place information
    """
    for place in petri_net['places']:
        if place['id'] == place_id:
            return place

    return None


def get_transition_info(petri_net, transition_id):
    """
    Given a Petri net and a transition ID, return the transition information
    """
    for transition in petri_net['transitions']:
        if transition['id'] == transition_id:
            return transition

    return None


def get_pending_decisions(petri_net, marking):
    # This function should analyze the petri_net and marking to find pending gateways
    # For simplicity, we will return a mock dictionary
    active_places = [place for place in marking if marking[place]['token'] > 0]
    pending_decisions = {}

    for place in active_places:
        place_info = get_place_info(petri_net, place)
        region_label = place_info['label']
        if place_info['region_type'] not in ['choice', 'nature', 'loop']:
            # skip non-gateway places
            continue
        if marking[place]['age'] < place_info.get('duration', 0.0):
            # skip if not yet ready
            continue

        choices = get_choices_for_exclusive_gateway(petri_net, place_info['id'])
        if choices:
            pending_decisions[region_label] = choices

    return pending_decisions


