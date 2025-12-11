import argparse
import os
import shutil
import sys
from datetime import datetime
from typing import Dict, Tuple, List, Union

CATEGORY_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "Math": ("math", "mathematics", "calculus", "calc", "algebra", "geometry"),
    "English": ("english", "comp", "composition", "eng", "lit", "literature"),
    "Science": ("science", "biology", "chemistry", "physics"),
    "History": ("history", "hist", "government", "civics", "gov", "social studies"),
    "Language": ("spanish", "french", "german", "language", "lang"),
    "Art": ("art", "drawing", "painting", "sketch"),
    "Documents": ("doc", "docx", "pdf", "txt"),
    "Images": ("jpg", "jpeg", "gif", "png"),
}

MIN_FILES_TO_KEEP_CATEGORY = 3


def get_directory_files(path: str) -> List[str]:
    try:
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def determine_categories(file_name: str) -> List[str]:
    name_lower = file_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return [category]
    return ["Other"]


def create_folder(path: str, folder_name: str, dry_run: bool = False) -> Union[str, None]:
    folder_path = os.path.join(path, folder_name)
    try:
        if os.path.exists(folder_path):
            return folder_path
        if dry_run:
            print(f"[DRY-RUN] Would create folder: {folder_path}")
            return folder_path
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
        return folder_path
    except Exception as e:
        print(f"[ERROR] folder not able to be created {folder_name}: {e}")
        return None


def move_file(file_path: str, destination_path: str, dry_run: bool = False) -> None:
    try:
        if dry_run:
            print(f"[DRY-RUN] Would move: {os.path.basename(file_path)} → {destination_path}")
            return
        shutil.move(file_path, destination_path)
        print(f"Moved: {os.path.basename(file_path)} → {destination_path}")
    except Exception as e:
        print(f"Could not move file: {file_path} → {destination_path}: {e}")


def organize_files(path: str, dry_run: bool = False) -> None:
    print("\n--- FILE ORGANIZER ---")
    files = get_directory_files(path)
    if not files:
        print("No files to organize.")
        return

    # Show categories that will be created
    print("\nCategory folders being created:")
    for file_path in files:
        file_name = os.path.basename(file_path)
        category = determine_categories(file_name)[0]
        print(f" - {category}")

    confirm = input("\nOrganize these files? (y/n): ").lower().strip()
    if confirm != "y":
        print("Task Completed. Files were not moved.")
        return

    category_file_count: Dict[str, int] = {}

    for file_path in files:
        file_name = os.path.basename(file_path)
        categories = determine_categories(file_name)
        for category in categories:
            category_folder = create_folder(path, category, dry_run=dry_run)
            try:
                timestamp = os.path.getmtime(file_path)
                month_folder_name = datetime.fromtimestamp(timestamp).strftime("%Y-%m")
            except Exception:
                month_folder_name = "UnknownMonth"

            month_folder = None
            if category_folder:
                month_folder = create_folder(category_folder, month_folder_name, dry_run=dry_run)

            if month_folder:
                move_file(file_path, month_folder, dry_run=dry_run)

            category_file_count[category] = category_file_count.get(category, 0) + 1

    # Merge small categories into Misc
    for category, count in category_file_count.items():
        if count < MIN_FILES_TO_KEEP_CATEGORY and category != "Misc":
            category_folder = os.path.join(path, category)
            misc_folder = create_folder(path, "Misc", dry_run=dry_run)
            try:
                for root, _, files_in_cat in os.walk(category_folder):
                    for f in files_in_cat:
                        fp = os.path.join(root, f)
                        move_file(fp, misc_folder, dry_run=dry_run)
                if dry_run:
                    print(f"[DRY-RUN] Would remove folder: {category_folder}")
                else:
                    shutil.rmtree(category_folder)
                    print(f"Category '{category}' moved into Misc")
            except Exception as e:
                print(f"[ERROR] Could not merge {category} into Misc: {e}")


def load_categories_from_file() -> None:
    global CATEGORY_KEYWORDS
    if not os.path.exists("categories.txt"):
        return
    try:
        with open("categories.txt", "r", encoding="utf-8") as f:
            CATEGORY_KEYWORDS = {}
            for line in f:
                if ":" in line:
                    category, keywords = line.strip().split(":", 1)
                    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
                    CATEGORY_KEYWORDS[category] = tuple(kw_list)
        print("Loaded categories from categories.txt")
    except Exception as e:
        print(f"ERROR Category settings could not be loaded: {e}")


def save_categories_to_file() -> None:
    try:
        with open("categories.txt", "w", encoding="utf-8") as f:
            for category, keywords in CATEGORY_KEYWORDS.items():
                f.write(f"{category}: {', '.join(keywords)}\n")
        print("Categories have been saved to categories.txt")
    except Exception as e:
        print(f"ERROR Category settings could not be saved: {e}")


def preview_structure(path: str) -> None:
    files = get_directory_files(path)
    counts: Dict[str, int] = {}
    for fp in files:
        cat = determine_categories(os.path.basename(fp))[0]
        counts[cat] = counts.get(cat, 0) + 1
    print("\nPreview of categories and file counts:")
    for cat, cnt in counts.items():
        print(f" - {cat}: {cnt}")


def add_custom_categories() -> None:
    print("\nCurrent categories list:")
    for cat in CATEGORY_KEYWORDS:
        print(" -", cat)
    choice = input("\nAdd a custom category? (y/n): ").lower().strip()
    if choice != "y":
        return
    while True:
        new_cat = input("\nProvide the custom category name: ").strip()
        if not new_cat:
            print("Category name field is not allowed to be blank.")
            continue
        keywords = input(
            "Provide the keywords for this new custom category (comma-separated): "
        ).lower().strip()
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        if not keyword_list:
            print("One or more keywords are required.")
            continue
        CATEGORY_KEYWORDS[new_cat] = tuple(keyword_list)
        print(f"Added category '{new_cat}' with keywords: {keyword_list}")
        more = input("\nWould you like to add another category? (y/n): ").lower().strip()
        if more != "y":
            break
    save_categories_to_file()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize the files into category folders and month subfolders"
    )
    parser.add_argument("folder", nargs="?", help="Folder path to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without making changes")
    parser.add_argument("--min", type=int, help="Minimum files needed to keep a category")
    return parser.parse_args()


def print_explainer() -> None:
    print(" DETAILED FILE ORGANIZER ")
    print("The program will:")
    print(" 1. Inspect the folder you choose")
    print(" 2. Identify the categories based on each of the file names")
    print(" 3. It will automatically make a folder for each category")
    print(" 4. Subfolders are made by the month the file was modified")
    print(" 5. Files are moved into their respective folders")
    print(" 6. If you choose, you can combine the small categories into Misc")
    print("Confirmation will be needed before any changes are made.")


if __name__ == "__main__":
    args = _parse_args()
    load_categories_from_file()
    print_explainer()
    if args.min is not None:
        MIN_FILES_TO_KEEP_CATEGORY = args.min
    print(f"\n[SETTINGS] Minimum files per category set to: {MIN_FILES_TO_KEEP_CATEGORY}")

    folder_to_sort = args.folder or input("folder path to organize: ")
    if not os.path.exists(folder_to_sort):
        print("[ERROR] This folder does not exist.")
        sys.exit(1)

    add_custom_categories()
    preview_structure(folder_to_sort)
    proceed = input("\nWould you like to proceed with organizing these files? (y/n): ").lower().strip()
    if proceed != "y":
        print("Task Completed.")
        sys.exit(0)
    organize_files(folder_to_sort, dry_run=args.dry_run)
