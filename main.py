import csv
from collections import defaultdict
import pandas as pd

def transform_dataframes(volunteers_df, applicants_df, columns_to_compare):
    for column in columns_to_compare:
        unique_values = pd.concat([volunteers_df[column], applicants_df[column]]).unique()
        mapping = {value: i + 1 for i, value in enumerate(unique_values)}

        volunteers_df[column] = volunteers_df[column].map(mapping)
        applicants_df[column] = applicants_df[column].map(mapping)

def calculate_similarity(volunteer, applicant, columns_to_compare):
    return sum(volunteer[column] == applicant[column] for column in columns_to_compare)

def match_applicants(volunteers, applicants, columns_to_compare):
    points_dict = {}

    for volunteer in volunteers:
        for applicant in applicants:
            pair_key = (volunteer['Nome'], applicant['Nome'])
            points = calculate_similarity(volunteer, applicant, columns_to_compare)
            points_dict[pair_key] = points

    return points_dict

def read_matching_result(filename='matching_result.csv'):
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header
            return sorted([(eval(row[0]), int(row[1])) for row in reader], key=lambda x: x[1], reverse=True)
    except FileNotFoundError:
        return []

def assign_volunteers(data):
    assignments = {}
    volunteer_counts = defaultdict(int)

    for pair, points in data:
        volunteer, applicant = pair

        if applicant not in assignments:
            assignments[applicant] = volunteer
            volunteer_counts[volunteer] += 1
        else:
            existing_points = assignments.get((applicant, assignments[applicant]), 0)

            if points == existing_points and volunteer_counts[volunteer] < volunteer_counts[assignments[applicant]]:
                volunteer_counts[assignments[applicant]] -= 1
                assignments[applicant] = volunteer
                volunteer_counts[volunteer] += 1

    return assignments

def main_menu():
    volunteers_filename = input("Enter the CSV file name for volunteers/employees: ")
    applicants_filename = input("Enter the CSV file name for applicants: ")

    volunteers_df = pd.read_csv(volunteers_filename)
    applicants_df = pd.read_csv(applicants_filename)

    columns_to_compare = ['Estado', 'Vivência (Remoto/Presencial)', 'Área de Interesse', 'Habilidade Técnica 1',
                           'Habilidade Técnica 3', 'Habilidade Técnica 5', 'Experiência Profissional', 'Idioma Extra',
                           'Educação', 'Soft Skill 1', 'Soft Skill 2']

    transform_dataframes(volunteers_df, applicants_df, columns_to_compare)

    result = match_applicants(volunteers_df.to_dict('records'), applicants_df.to_dict('records'), columns_to_compare)

    data = read_matching_result()

    assignments_choice = input("Do you want assignments for all volunteers or a specific one? (all/volunteer/exit): ").lower()

    if assignments_choice == 'exit':
        print("Exiting the program.")
        return
    elif assignments_choice == 'all':
        assignments = assign_volunteers(data)
        print("Assignments for all volunteers have been generated.")
    elif assignments_choice == 'volunteer':
        specific_volunteer = input("Enter the name of the specific volunteer: ")
        specific_data = [(pair, points) for pair, points in data if pair[0] == specific_volunteer]
        assignments = assign_volunteers(specific_data)
        print(f"Assignments for {specific_volunteer} have been generated.")
    else:
        print("Invalid choice. Exiting.")
        return

    output_filename = input("Enter the CSV file name for the assignments (e.g., results.csv): ")

    assignments_df = pd.DataFrame(list(assignments.items()), columns=['Applicant', 'Volunteer'])

    assignments_df.to_csv(output_filename, index=False)
    print(f"Assignments have been saved to {output_filename}.")

if __name__ == "__main__":
    main_menu()
