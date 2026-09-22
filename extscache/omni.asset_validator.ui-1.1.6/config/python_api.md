# Public API for module omni.asset_validator.ui:

## Classes

- class AssetMode(IntEnum)
  - Uri: int
  - Stage: int

- class PublicExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def show(self)
  - def hide(self)
  - def visible(self) -> bool
  - [property] def variants(self) -> bool
  - [variants.setter] def variants(self, flag: bool)
  - [property] def issueOnRootOnly(self) -> bool
  - [issueOnRootOnly.setter] def issueOnRootOnly(self, flag: bool)
  - [property] def selectedIssues(self) -> list[omni.asset_validator.core.Issue]
  - def enableRule(self, Rule: omni.asset_validator.core.BaseRuleChecker)
  - def disableRule(self, Rule: omni.asset_validator.core.BaseRuleChecker)
  - def enabled(self, Rule: omni.asset_validator.core.BaseRuleChecker) -> bool
  - def reset(self, resetAssets: bool = False, resetRules: bool = False)
  - def getAssetMode(self) -> AssetMode
  - def setAssetMode(self, mode: AssetMode)
  - def getAssetUri(self) -> str
  - def setAssetUri(self, asset: str)
  - def getStage(self) -> Usd.Stage
  - def setStage(self, stage: Usd.Stage)
  - async def validate_async(self) -> list[omni.asset_validator.core.Results]
  - def selectIssue(self, issue: omni.asset_validator.core.Issue) -> bool
  - async def fix(self)
  - async def fixAndSave(self)
  - async def fixIssue(self, issue: omni.asset_validator.core.Issue)
  - async def fixAndSaveIssue(self, issue: omni.asset_validator.core.Issue)

## Functions

- def get_instance() -> PublicExtension
