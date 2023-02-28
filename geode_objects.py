import opengeode as og
import opengeode_io as og_io
import opengeode_geosciences as og_gs
import opengeode_geosciencesio as og_gs_io
import geode_viewableobjects as g_vo

def objects_list():
    return {
        "BRep": {
            "input": [ og.BRepInputFactory ],
            "output": [ og.BRepOutputFactory ],
            "load": og.load_brep,
            "save": og.save_brep,
            "save_viewable": g_vo.save_viewable_brep
        },
        "CrossSection": {
            "input": [ og_gs.CrossSectionInputFactory ],
            "output": [ og.SectionOutputFactory, og_gs.CrossSectionOutputFactory ],
            "load": og_gs.load_cross_section,
            "save": og_gs.save_cross_section,
            "save_viewable": ""
        },
        "EdgedCurve2D": {
            "input": [ og.EdgedCurveInputFactory2D ],
            "output": [ og.EdgedCurveOutputFactory2D ],
            "load": og.load_edged_curve2D,
            "save": og.save_edged_curve2D,
            "save_viewable": g_vo.save_viewable_edged_curve2D
        },
        "EdgedCurve3D": {
            "input": [ og.EdgedCurveInputFactory3D ], 
            "output": [ og.EdgedCurveOutputFactory3D ], 
            "load": og.load_edged_curve3D, 
            "save": og.save_edged_curve3D, 
            "save_viewable": g_vo.save_viewable_edged_curve3D
        },
        "Graph": {
            "input": [ og.GraphInputFactory ], 
            "output": [ og.GraphOutputFactory ], 
            "load": og.load_graph, 
            "save": og.save_graph, 
            "save_viewable": ""
        },
        "HybridSolid3D": {
            "input": [ og.HybridSolidInputFactory3D ], 
            "output": [ og.HybridSolidOutputFactory3D ], 
            "load": og.load_hybrid_solid3D, 
            "save": og.save_hybrid_solid3D, 
            "save_viewable": g_vo.save_viewable_hybrid_solid3D
        },
        "PointSet2D": {
            "input": [ og.PointSetInputFactory2D ], 
            "output": [ og.PointSetOutputFactory2D ], 
            "load": og.load_point_set2D, 
            "save": og.save_point_set2D, 
            "save_viewable": g_vo.save_viewable_point_set2D
        },
        "PointSet3D": {
            "input": [ og.PointSetInputFactory3D ],
            "output": [ og.PointSetOutputFactory3D ], 
            "load": og.load_point_set3D, 
            "save": og.save_point_set3D, 
            "save_viewable": g_vo.save_viewable_point_set3D
        },
        "PolygonalSurface2D": {
            "input": [ og.PolygonalSurfaceInputFactory2D ], 
            "output": [ og.PolygonalSurfaceOutputFactory2D ], 
            "load": og.load_polygonal_surface2D, 
            "save": og.save_polygonal_surface2D, 
            "save_viewable": g_vo.save_viewable_triangulated_surface2D
        },
        "PolygonalSurface3D": {
            "input": [ og.PolygonalSurfaceInputFactory3D ], 
            "output": [ og.PolygonalSurfaceOutputFactory3D ], 
            "load": og.load_polygonal_surface3D, 
            "save": og.save_polygonal_surface3D, 
            "save_viewable": g_vo.save_viewable_triangulated_surface3D
        },
        "PolyhedralSolid3D": {
            "input": [ og.PolyhedralSolidInputFactory3D ], 
            "output": [ og.PolyhedralSolidOutputFactory3D ], 
            "load": og.load_polyhedral_solid3D, 
            "save": og.save_polyhedral_solid3D, 
            "save_viewable": g_vo.save_viewable_polyhedral_solid3D
        },
        "RegularGrid2D": {
            "input": [ og.RegularGridInputFactory2D ],
            "output": [ og.RegularGridOutputFactory2D ], 
            "load": og.load_regular_grid2D, 
            "save": og.save_regular_grid2D, 
            "save_viewable": ""
        },
        "RegularGrid3D": {
            "input": [ og.RegularGridInputFactory3D ], 
            "output": [ og.RegularGridOutputFactory3D ], 
            "load": og.load_regular_grid3D, 
            "save": og.save_regular_grid3D, 
            "save_viewable": g_vo.save_viewable_regular_grid3D
        },
        "Section": {
            "input": [ og.SectionInputFactory ], 
            "output": [ og.SectionOutputFactory ], 
            "load": og.load_section, 
            "save": og.save_section, 
            "save_viewable": g_vo.save_viewable_section 
        },
        "StructuralModel": {
            "input": [ og_gs.StructuralModelInputFactory ],
            "output": [ og.BRepOutputFactory, og_gs.StructuralModelOutputFactory ], 
            "load": og_gs.load_structural_model, 
            "save": og_gs.save_structural_model, 
            "save_viewable": g_vo.save_viewable_brep
        },
        "TetrahedralSolid3D": {
            "input": [ og.TetrahedralSolidInputFactory3D ], 
            "output": [ og.TetrahedralSolidOutputFactory3D ], 
            "load": og.load_tetrahedral_solid3D,
            "save": og.save_tetrahedral_solid3D, 
            "save_viewable": g_vo.save_viewable_tetrahedral_solid3D
        },
        "TriangulatedSurface2D": {
            "input": [ og.TriangulatedSurfaceInputFactory2D ],
            "output": [ og.TriangulatedSurfaceOutputFactory2D ], 
            "load": og.load_triangulated_surface2D, 
            "save": og.save_triangulated_surface2D, 
            "save_viewable": g_vo.save_viewable_brep
        },
        "TriangulatedSurface3D": {
            "input": [ og.TriangulatedSurfaceInputFactory3D ], 
            "output": [ og.TriangulatedSurfaceOutputFactory3D ], 
            "load": og.load_triangulated_surface3D, 
            "save": og.save_triangulated_surface3D, 
            "save_viewable": g_vo.save_viewable_triangulated_surface3D
        },
        "VertexSet": {
            "input": [ og.VertexSetInputFactory ], 
            "output": [ og.VertexSetOutputFactory ], 
            "load": og.load_vertex_set, 
            "save": og.save_vertex_set, 
            "save_viewable": ""
        }
    }