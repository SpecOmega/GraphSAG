from __future__ import annotations
class DeepSeekV4Adapter:
    """Protocol boundary only. Authorization must never depend on an LLM response alone."""
    def __init__(self,base_url:str,api_key:str|None=None,model:str='deepseek-v4'): self.base_url=base_url; self.api_key=api_key; self.model=model
    async def complete(self,messages,**kwargs):
        raise NotImplementedError('Wire this adapter to the approved DeepSeek V4-compatible endpoint; keep credentials outside source control.')
