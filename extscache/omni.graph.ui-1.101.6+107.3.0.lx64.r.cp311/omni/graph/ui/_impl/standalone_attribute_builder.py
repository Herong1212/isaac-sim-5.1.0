from typing import Any

import carb
import omni.graph.core as og
import omni.ui as ui
import omni.usd
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from pxr import Sdf, Usd

from .compute_node_widget import ComputeNodeWidgetUtils
from .omnigraph_attribute_models import (
    OmniGraphAttributeModel,
    OmniGraphGfMatrixAttributeModel,
    OmniGraphGfQuatAttributeModel,
    OmniGraphGfVecAttributeModel,
    OmniGraphTfTokenAttributeModel,
)


class StandaloneAttributeBuilder:
    @staticmethod
    def build_ui(
        attribute: og.Attribute, label_kwd_args: dict[str, Any] = None, value_kwd_args: dict[str, Any] = None
    ) -> tuple[ui.Container, ui.AbstractValueModel]:
        """
        Create UI for displaying the runtime value of an OmniGraph attribute and updating it as it changes.

        The returned UI is independent of the property window and can be used in any window or container widget.
        By default the UI for input attributes allows editing the value while output attributes are display-only.
        The value in the UI is the runtime value of the attribute from Fabric, not the authored USD value.

        Args:
            attribute:      OmniGraph attribute to create UI for.

            label_kwd_args: Dictionary of keyword arguments to be used when creating the label. These are applied after
                            the attribute builder's defaults and can thus be used to override them.

            value_kwd_args: Dictionary of keyword arguments to be used when creating the widget used to display the
                            attribute's value. These are applied after the attribute builder's defaults and can thus be
                            used to override them. The set of valid keywords depends upon the type of widget used for
                            the attribute value. Unfortunately that information is buried deep within the
                            omni.kit.property.usd extension so your best bet is to make an educated guess and then
                            use trial and error.

                            In addition the following special keyword is supported:

                            no_control_state: bool
                                The control state widget is the little box to right of the value that shows whether
                                attribute the has changed from its default, is connected, etc. Set this True to prevent
                                it being drawn.

        Returns:
            A tuple consisting of the container widget holding the attribute's UI and the model which
            manages the value displayed. If the widget has multiple components then the parent model will be returned.
            If the attribute is not of type which can be displayed (e.g. an execution pin or bundle) then None will
            be returned.

        Raises:
            omni.graph.core.OmniGraphAttributeError if attribute is valid but cannot be found on the node. Basically
            means that the graph is corrupt.
        """
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        attr_path: Sdf.Path = Sdf.Path(attribute.get_path())
        usd_attr: Usd.Attribute = stage.GetAttributeAtPath(attr_path)
        if not usd_attr.IsValid():
            carb.log_warn(f"Could not find USD property for OmniGraph attribute {attribute.get_path()}.")
            return None

        prop_ui = UsdPropertyUiEntry(
            usd_attr.GetName(), usd_attr.GetDisplayGroup(), usd_attr.GetAllMetadata(), type(usd_attr)
        )
        attr = ComputeNodeWidgetUtils.customize_prop_metadata(attribute.get_node(), prop_ui)
        if attr is None:
            # This should never happen.
            raise og.OmniGraphAttributeError(f"Could not find OmniGraph attribute for {attr_path.pathString}.")

        container, model = ComputeNodeWidgetUtils.build_property_item(
            stage, prop_ui, attr_path.GetPrimPath(), label_kwd_args, value_kwd_args
        )
        return (container, model)

    @staticmethod
    def get_value_as_string(value_model: ui.AbstractValueModel, elide_big_array: bool = False) -> str:
        """
        Get the current value from a model returned by build_ui(), in string form.

        Args:
            value_model     - Model to retrieve the value from
            elide_big_array - For arrays with a large number of elements, replace the middle elements with "..."

        Returns:
            String representation of the model's current value.

        Raises:
            TypeError if 'value_model' is not a supported type.
        """
        # This is similar to code in omni.kit.property.usd's AttributeContextMenu._register_copy_paste_menus() so if
        # things break you might want to look there for recent changes that should be applied here as well.
        if isinstance(value_model, OmniGraphAttributeModel):
            value_str = value_model.get_value_as_string(elide_big_array=elide_big_array)
        elif isinstance(value_model, OmniGraphTfTokenAttributeModel):
            value_str = value_model.get_value_as_token()
        elif isinstance(value_model, OmniGraphGfVecAttributeModel):
            value_str = str(value_model._construct_vector_from_item())  # noqa: protected-access
        elif isinstance(value_model, OmniGraphGfMatrixAttributeModel):
            value_str = str(value_model._construct_matrix_from_item())  # noqa: protected-access
        elif isinstance(value_model, OmniGraphGfQuatAttributeModel):
            value_str = str(value_model._construct_quat_from_item())  # noqa: protected-access
        else:
            raise TypeError("Unsupported value model type.")
        return value_str

    @staticmethod
    def is_attribute_supported(attribute: og.Attribute) -> bool:
        """
        Returns True if UI can be built for the attribute's type.
        """
        # It has to be a USD Attribute, not a relationship.
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        attr_path: Sdf.Path = Sdf.Path(attribute.get_path())
        usd_attr: Usd.Attribute = stage.GetAttributeAtPath(attr_path)
        return usd_attr.IsValid()
