import os
import re
import config

def generate_live_svgs(local_signals, local_attributes):
    """
    Loops through every page specified in config.DASHBOARD_PAGES,
    reads the main source blueprint SVG file, replaces data placeholders, 
    and returns a lookup dictionary of the updated SVG strings mapped by their real filenames.
    """
    processed_pages = {}

    for page in config.DASHBOARD_PAGES:
        # Using the direct path to your main source SVG file
        template_path = page["template"]
        
        # Extract just the raw file name (e.g., "main_layout.svg") to use as our memory key
        filename_key = os.path.basename(template_path)

        if not os.path.exists(template_path):
            print(f"[Processor Error] Blueprint template asset missing: {template_path}")
            continue

        try:
            # 1. Read clean raw master structural vector layer from the main SVG file
            with open(template_path, "r", encoding="utf-8") as f:
                working_svg = f.read()

            # 2. Swap placeholder tags with active thread telemetry
            for key, placeholder in config.SVG_TEXT_MAP.items():
                value = "---"  # Default configuration status
                
                if key in local_signals:
                    val_raw = local_signals[key]
                    value = f"{val_raw:.2f}" if isinstance(val_raw, (int, float)) else str(val_raw)
                elif key in local_attributes:
                    val_raw = local_attributes[key]
                    if isinstance(val_raw, bool):
                        value = "ON" if val_raw else "OFF"
                    else:
                        value = f"{val_raw:.2f}" if isinstance(val_raw, (int, float)) else str(val_raw)

                working_svg = working_svg.replace(placeholder, value)

            # 3. Strip nested standard web font wrappers that break cross-rendering
            working_svg = re.sub(r'<font[^>]*>', '', working_svg)
            working_svg = re.sub(r'</font>', '', working_svg)

            # 4. Map the raw XML text directly to its main filename key in memory
            processed_pages[filename_key] = working_svg

        except Exception as e:
            print(f"Failed parsing dynamic layouts for target page {filename_key}: {e}")

    return processed_pages