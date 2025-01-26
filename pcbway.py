import csv
import requests
import sys

def fetch_lcsc_data(part_number):
    url = f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={part_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://lcsc.com/",
        "Origin": "https://lcsc.com"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data and data.get("code") == 200 and "result" in data:
        return data["result"]  # Return the result section
    return {}

def process_bom(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["Item #", "Designator", "Qty", "Manufacturer", "Mfg Part #", "Description / Value", "Footprint", "Package", "Type", "LCSC Part #", "Your Instructions / Notes"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, row in enumerate(reader, start=1):
            lcsc_number = row.get("LCSC")
            if not lcsc_number:
                continue

            lcsc_data = fetch_lcsc_data(lcsc_number)

            encap_standard = lcsc_data.get("encapStandard", "")
            part_type = "Plugin" if encap_standard.startswith("Plugin") else "SMD"

            writer.writerow({
                "Item #": i,
                "Designator": row.get("Designator"),
                "Qty": row.get("Quantity"),
                "Manufacturer": lcsc_data.get("brandNameEn", ""),
                "Mfg Part #": lcsc_data.get("productModel", ""),
                "Description / Value": lcsc_data.get("productIntroEn", ""),
                "Footprint": row.get("Footprint"),
                "Package": encap_standard,
                "Type": part_type,
                "LCSC Part #": lcsc_number,
                "Your Instructions / Notes": ""
            })

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_bom(input_file, output_file)

