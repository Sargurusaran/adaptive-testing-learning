import csv
import math

def main():
    # Load the item database
    item_db = read_item_db('ml_mcq_db.csv')  # item database (dictionary)

    s = 0  # scored response
    r = []  # list of scored responses
    i = [item_db["coditem"][0]]  # code of item administered
    bs = [item_db["b"][0]]  # item difficulties

    sem_theta = 0.70  # Initial theta with some standard error
    max_items = 18
    resp = ""

    asked_items = set()  # To track the items already asked

    # Initialize theta (current estimate and standard error)
    theta = [sem_theta, 0.0]

    # Introduction and initial item administration
    print('Hello! I am ML_CAT, a Computerized Adaptive Test for Machine Learning knowledge assessment!')
    print("I am a simple program designed to adaptively assess your understanding of machine learning concepts.")
    print()
    name = input("What is your name? ")
    print("Hi " + name + ". Ready to test your ML knowledge?")
    print()
    print("I will present multiple-choice questions and ask you to select the correct answer.")
    print()
    print(item_db["item"][0])
    print()
    for idx, option in enumerate(item_db["options"][0], start=1):
        print(f"{idx}. {option}")
    print()
    resp = input("Enter the number corresponding to your answer: ")
    print()

    # First pass: score the initial item
    s = score(resp, item_db["key"][0])
    r.append(s)
    asked_items.add(item_db["coditem"][0])  # Mark the first question as asked

    if s == 1:
        print("Correct! Let's proceed with the test.")
    else:
        print(f"Incorrect. The correct answer is {item_db['key'][0]}. Let's continue with the test.")

    # Remove the first item from the dictionary (these are removed in place)
    remove_item(item_db, 0)

    # Adaptive testing loop
    while len(r) < max_items:
        if len(bs) > 0:
            theta = estimate_theta(r, bs, theta)  # Pass theta to the function
            next_i = next_item(theta[0], item_db, r, bs, asked_items)
        else:
            print("Error: Difficulty list is empty.")
            return

        if next_i:
            print(next_i["item"])
            for idx, option in enumerate(next_i["options"], start=1):
                print(f"{idx}. {option}")
            print()
            resp = input("Enter the number corresponding to your answer: ")
            print()
            asked_items.add(next_i["coditem"])  # Mark the current question as asked
        else:
            print("No suitable question found. The test is complete or there are no more questions.")
            break

        s = score(resp, next_i["key"])

        if s == 1:
            yn = input("Correct! Type 'y' for the next item or 'n' to quit: ")
        else:
            yn = input(f"Incorrect. The correct answer is {next_i['key']}. Type 'y' for the next item or 'n' to quit: ")

        if yn.lower() == 'n':
            break

        r.append(s)
        bs.append(next_i["b"])
        i.append(next_i["coditem"])

    # Final score summary
    print()
    print("Congratulations! You completed the ML CAT test.")
    print(f"You answered {len(r)} items.")
    print(f"You got {sum(r)} correct.")
    if len(bs) > 0:
        theta = estimate_theta(r, bs, theta)
        print(f"Your IRT theta score is {round(theta[0], 2)}, with SEM = {round(theta[1], 2)}.")
        standardized_score = round(((theta[0] - 1.40) / 1.50) * 15) + 100
        print(f"Your standardized score (M=100, SD=15, like in IQ tests) is {standardized_score}.")
    else:
        print("Not enough data to calculate theta score.")

def score(resp, key):
    # Check if the selected answer is correct
    return 1 if resp == key else 0

def next_item(theta, item_db, r, bs, asked_items):
    """
    Selects the next item based on the user's performance and item difficulty,
    ensuring that no question is repeated.

    Args:
        theta: Current estimated ability level.
        item_db: Item database.
        r: List of correct/incorrect responses.
        bs: List of item difficulties.
        asked_items: Set of items already asked.

    Returns:
        The next item to be administered, or None if no suitable item is found.
    """

    # Calculate the expected difficulty level for the next item
    target_difficulty = theta + 0.5 * (r[-1] - 0.5)  # Adjust based on last response

    # Sort items by the absolute difference between their difficulty and the target difficulty,
    # prioritizing items that haven't been asked yet
    sorted_items = sorted(zip(item_db['coditem'], item_db['b'], item_db['item'], item_db['options'], item_db['key']),
                           key=lambda x: (abs(x[1] - target_difficulty), x[0] not in asked_items))

    for item in sorted_items:
        if item[0] not in asked_items:
            return {'coditem': item[0], 'b': item[1], 'item': item[2], 'options': item[3], 'key': item[4]}

    return None  # No suitable item found

def estimate_theta(r, b, th):
    # IRT theta estimation
    conv = 0.001
    J = len(r)
    se = 10.0
    delta = conv + 1
    th = float(th[0])

    th_max = max(b) + 0.5
    th_min = min(b) - 0.5

    if sum(r) == J:
        th = th_max
    elif sum(r) == 0:
        th = th_min
    else:
        while abs(delta) > conv:
            sumnum, sumdem = 0.0, 0.0
            for j in range(J):
                phat = 1 / (1.0 + math.exp(-1 * (th - b[j])))

                sumnum += (r[j] - phat)
                sumdem -= phat * (1.0 - phat)
            delta = sumnum / sumdem
            th -= delta
            se = 1 / math.sqrt(-sumdem)

    return [th, se]

def remove_item(item_db, index):
    # Remove item from all lists in the item_db
    item_db['coditem'].pop(index)
    item_db['b'].pop(index)
    item_db['item'].pop(index)
    item_db['options'].pop(index)
    item_db['key'].pop(index)

def read_item_db(file):
    # Load item data from a CSV file
    with open(file) as filename:
        file = csv.DictReader(filename)
        coditem, b, item, options, key = [], [], [], [], []

        for col in file:
            coditem.append(col['coditem'])
            b.append(float(col['b']))
            item.append(col['item'])
            options.append(col['options'].split(';'))  # Split options into a list
            key.append(col['key'])

        return {
            'coditem': coditem,
            'b': b,
            'item': item,
            'options': options,
            'key': key
        }

if __name__ == '__main__':
    main()
