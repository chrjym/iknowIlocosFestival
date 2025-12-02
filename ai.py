import pandas as pd

# Load Excel into a DataFrame (make sure the filename is correct)
df = pd.read_excel('Aidatabase.xlsx')

# Normalize column names
df.columns = [c.strip().lower() for c in df.columns]

# Convert to list of dicts (knowledge base)
facts = df.to_dict(orient='records')


def list_all_municipalities():
    municipalities = sorted({str(f['municipalities']).strip() for f in facts})
    print("\nAvailable municipalities:")
    for i, m in enumerate(municipalities, start=1):
        print(f"{i}. {m}")


def show_municipality_info(municipality: str):
    municipality = municipality.strip().lower()
    found = False

    print(f"\nInformation for municipality: {municipality.title()}")

    for f in facts:
        muni = str(f['municipalities']).strip().lower()
        if muni == municipality:
            fest_name = str(f['festival']).strip().rstrip(',')
            description = str(f['about that festival']).strip()
            print(f"\nFestival: {fest_name}")   
            print(f"Description: {description}")
            found = True

    if not found:
        print(f"\nNo data found for municipality '{municipality}'.")
        

def main():
    print("Welcome to Festival Info AI.")
    list_all_municipalities()  # show guide first

    while True:
        print("\nMenu:")
        print("1. Choose a municipality")
        print("2. Show municipalities again")
        print("3. Exit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == '1':
            muni = input("Enter municipality name: ").strip()
            show_municipality_info(muni)

        elif choice == '2':
            list_all_municipalities()

        elif choice == '3':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == '__main__':
    main()
