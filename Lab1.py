#!/usr/bin/env python3
import arcpy, os, sys

def find_feature_class(fc_name):
    """
    Search the workspace (including feature datasets) for a feature class matching fc_name.
    Returns the full path if found, else None.
    """
    workspace = arcpy.env.workspace
    # Search root
    fcs_root = arcpy.ListFeatureClasses() or []
    for fc in fcs_root:
        if fc.lower() == fc_name.lower():
            return os.path.join(workspace, fc)
    # Search feature datasets
    fds = arcpy.ListDatasets(feature_type='Feature') or []
    for fd in fds:
        fcs = arcpy.ListFeatureClasses(feature_dataset=fd) or []
        for fc in fcs:
            if fc.lower() == fc_name.lower():
                return os.path.join(workspace, fd, fc)
    return None

def buffer_layer(input_name, buffer_distance, output_name):
    print(f"[BUFFER] {input_name} -> {output_name} ({buffer_distance} ft)")
    in_fc = find_feature_class(input_name)
    if not in_fc:
        raise RuntimeError(f"Feature class not found: {input_name}")
    out_fc = os.path.join(arcpy.env.workspace, output_name)
    arcpy.Buffer_analysis(
        in_features=in_fc,
        out_feature_class=out_fc,
        buffer_distance_or_field=f"{buffer_distance} Feet",
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="ALL"
    )
    return out_fc

def intersect_buffers(buffer_list, output_name):
    print(f"[INTERSECT] buffers -> {output_name}")
    out_fc = os.path.join(arcpy.env.workspace, output_name)
    arcpy.Intersect_analysis(in_features=buffer_list, out_feature_class=out_fc)
    return out_fc

def spatial_join(address_name, intersect_fc, output_name):
    print(f"[SPATIAL JOIN] {address_name} with {intersect_fc} -> {output_name}")
    addr_fc = find_feature_class(address_name)
    if not addr_fc:
        raise RuntimeError(f"Address feature class not found: {address_name}")
    out_fc = os.path.join(arcpy.env.workspace, output_name)
    arcpy.SpatialJoin_analysis(
        target_features=addr_fc,
        join_features=intersect_fc,
        out_feature_class=out_fc,
        join_type="KEEP_COMMON"
    )
    return out_fc

def count_features(feature_class):
    count = int(arcpy.GetCount_management(feature_class).getOutput(0))
    print(f"[COUNT] {os.path.basename(feature_class)}: {count}")
    return count

def main():
    # -- Configuration --
    workspace = r"C:\Users\paint\Documents\ArcGIS\Projects\WestNileOutbreak\WestNileOutbreak.gdb"
    if not arcpy.Exists(workspace):
        print(f"ERROR: Workspace does not exist: {workspace}", file=sys.stderr)
        sys.exit(1)
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    layers = [
        "Mosquito_Larval_Sites",
        "Wetlands",
        "Lakes_and_Reservoirs___Boulder_County",
        "OSMP_Properties"
    ]
    address_layer = "Addresses"
    buffer_outputs = []

    try:
        # Buffer each layer
        for layer in layers:
            dist_str = input(f"Enter buffer distance in feet for {layer}: ")
            try:
                dist = float(dist_str)
            except ValueError:
                print(f"Invalid distance '{dist_str}', defaulting to 0.")
                dist = 0
            out_name = f"{layer}_buffer_{int(dist)}ft"
            buf_fc = buffer_layer(layer, dist, out_name)
            buffer_outputs.append(buf_fc)

        # Intersect buffers
        if len(buffer_outputs) < 2:
            raise RuntimeError("Need at least two buffers to intersect.")
        intersect_fc = intersect_buffers(buffer_outputs, "HighRisk_Intersect")

        # Spatial join addresses
        joined_fc = spatial_join(address_layer, intersect_fc, "Joined_Addresses")

        # Count at-risk addresses
        count_features(joined_fc)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()