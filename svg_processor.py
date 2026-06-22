import os
import re
import config

def generate_live_svgs(local_signals, local_attributes):
    """
    Loops through every page specified in config.DASHBOARD_PAGES,
    replaces data placeholders, and saves them directly to the svg_cache folder.
    """
    # Double check that cache directory folder path exists
    os.makedirs(config.CACHE_DIR, exist_ok=True)

    for page in config.DASHBOARD_PAGES:
        template_path = page["template"]
        output_path = os.path.join(config.CACHE_DIR, page["live_filename"])

        if not os.path.exists(template_path):
            print(f"[Processor Error] Blueprint template asset missing: {template_path}")
            continue

        try:
            # 1. Read clean raw master structural vector layer
            with open(template_path, "r", encoding="utf-8") as f:
                working_svg = f.read()

            # 2. Swap placeholder tags with active thread telemetry
            for key, placeholder in config.SVG_TEXT_MAP.items():
                value = "---"  # Default pipeline configuration display status
                
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

            # 4. Save clean compiled framework live file down into cache directory
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(working_svg)

        except Exception as e:
            print(f"Failed parsing dynamic layouts for target page {page['page_id']}: {e}")