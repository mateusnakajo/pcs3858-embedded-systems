from math import acos, cos, hypot, pi

from models.event import *

HALT_ENGINE_INPUT = (0, EngineDirection.FORWARD)
HALT_ENGINE_EVENT = EngineInput(HALT_ENGINE_INPUT, HALT_ENGINE_INPUT)


def is_on_right_half(x, y):
    return x >= 0


def is_on_left_half(x, y):
    return not is_on_right_half(x, y)


def is_on_upper_half(x, y):
    return y >= 0


def is_on_bottom_half(x, y):
    return not is_on_upper_half(x, y)


def to_engine_inputs(left, right, intensity):
    left_direction = EngineDirection.BACKWARD if left < 0 else EngineDirection.FORWARD
    right_direction = EngineDirection.BACKWARD if right < 0 else EngineDirection.FORWARD
    left_input = (round(abs(left * intensity), 2), left_direction)
    right_input = (round(abs(right * intensity), 2), right_direction)

    return left_input, right_input

def relative_intensity_of_auxiliary_engine(x, y, intensity):
    '''
    Given a point (x, y) and their hypotenuse, return what strength to apply to
    the auxiliary motor.
    '''

    try:
        x_relative = abs(x / intensity)
    except ZeroDivisionError:
        return 0

    # aux = 1 - 2 * x_relative                # Naive solution, not symmetrical
    # aux = (4 * acos(x_relative) - pi) / pi  # Linear movement, abrupt change on edges
    aux = -cos(2 * acos(x_relative))          # Natural movement
    return aux


def direction_event_to_engine_input(event: DirectionEvent):
    '''
    Get a position in a circle and transform into left/right engine powers.
    '''

    (x, y) = event.get_coordinates()
    intensity = hypot(x, y)

    l = 1
    r = relative_intensity_of_auxiliary_engine(x, y, intensity)
    assert abs(r) <= 1

    if is_on_left_half(x, y) ^ is_on_bottom_half(x, y):
        l, r = r, l

    if is_on_bottom_half(x, y):
        l = -l
        r = -r

    return EngineInput(*to_engine_inputs(l, r, min(intensity, 1)))


def _is_halt_event(event):
    return type(event) is HaltEvent


def _is_direction_event(event):
    return type(event) is DirectionEvent


def handle_event(event: InputEvent):
    if _is_halt_event(event):
        return HALT_ENGINE_EVENT

    elif _is_direction_event(event):
        return direction_event_to_engine_input(event)

    else:
        raise ValueError("Could not understand event type " +
                         type(event).__name__)
