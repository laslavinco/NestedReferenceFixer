import re
#todo:
    #ref node is changing properly now but its children are not so figure out a way to fix that.


import pymel.core as pm
# list the references which has parent references i.e. sub references.
references = [i for i in pm.listReferences(recursive=True) if i.refNode.parentReference()]

for ref in references:
    # check how many copies of those references are there in the scene file if more than one then go forward
    if len(ref.copyNumberList()) == 1:
        continue
        
    unused_namespace = get_unused_namespace(ref)
    clean_name = get_clean_name(ref)
    parent_reference = ref.refNode.parentReference()
    if parent_reference:
        parent_namespace = parent_reference.referenceFile().namespace
    if parent_reference:
        parent_reference.referenceFile().importContents()
        pm.namespace(collapseAncestors=ref.namespace)
        pm.namespace(mv=(parent_namespace, ":"), force=True)
        pm.namespace(rm=parent_namespace, force=True)
        
    old_ns = ref.nodes()[0].split(":")[0]
    cmds.file(ref.withCopyNumber(), e=True, force=True, ns=unused_namespace)
    ref.load()
    
    for edit in ref.getReferenceEdits():
        pm.mel.eval(edit.replace(old_ns+":", ref.namespace+":"))
    
    #pm.lockNode(ref.refNode, lock=False)
    #ref.refNode.rename("{}RN".format(clean_name))
    #pm.lockNode(ref.refNode, lock=True)
    
    cmds.namespace(set=':')
    
    
def get_unused_namespace(ref):
    
    clean_name = get_clean_name(ref)
    # list out all the references with similar path to check how many times this kind of reference is referenced.
    number_of_refs = sorted([i for i in pm.listReferences(recursive=True) if ref.path in i.path])
    # check the last copy number of last reference to predict next possible number.
    last_ref_number = number_of_refs[-1].withCopyNumber().replace(ref.path, "").replace("{", "").replace("}", "")
    unused_namespace = clean_name+str(int(last_ref_number)+1)

    return unused_namespace
    

def get_clean_name(ref):
    return ref.path.basename().splitext()[0]
