def wrapper(**kwargs):
    if "person_age" not in kwargs:
        print_vals(person_age=40, **kwargs)
    else:
        print_vals(**kwargs)


def print_vals(person_age, person_weight, person_gender):
    print(f"age={person_age}, weight={person_weight}, is_male={person_gender}")


def route():
    age = 5
    weight = 64.3
    is_male = True

    wrapper(person_age = age, person_weight = weight, person_gender = is_male)


route()
