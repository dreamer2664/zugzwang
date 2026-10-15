from pathlib import Path
import json,os,sys,tempfile,subprocess,contextlib,io,zipfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'ops'))
import field,release
class CommissionSafety(unittest.TestCase):
 def test_public_briefs_are_complete_clean_and_token_free(self):
  for p in (ROOT/'briefs').glob('*.md'):
   t=p.read_text();self.assertGreater(len(t.split()),1000);self.assertEqual(t.count('CHATCODE_TOKEN=PENDING-ISSUE'),1);self.assertEqual(t.count('GITHUB_TOKEN=PENDING-ISSUE'),1)
 def test_own_identity_fence(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):field.home('not-a-commissioned-agent',t)
 def test_failure_recovery_handoff_redacts_credential(self):
  agent=field.AGENTS[0]
  with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'GITHUB_TOKEN':'never-publish-unit-secret'}):
   field.event(agent,'failure','prototype','real failure',state='failed',root=t)
   field.event(agent,'fix','patched','retest passed',state='checkpoint',next_action='inspect actual output',root=t)
   log=(Path(t)/'agents'/agent/'HANDOFF.md').read_text();self.assertNotIn('never-publish-unit-secret',log);self.assertIn('real failure',log);self.assertIn('retest passed',log)
 def test_child_auth_isolation_and_actual_result(self):
  agent=field.AGENTS[0]
  with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'GITHUB_TOKEN':'secret-test'}),contextlib.redirect_stdout(io.StringIO()):
   rc=field.run_tracked(agent,[sys.executable,'-c','import os;print("CLEAN" if "GITHUB_TOKEN" not in os.environ else "LEAK")'],'test',root=t,interval=.03)
   self.assertEqual(rc,0);self.assertIn('CLEAN',(Path(t)/'agents'/agent/'HANDOFF.md').read_text())
 def test_missing_process_and_nonzero_are_not_success(self):
  agent=field.AGENTS[0]
  with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(field.run_tracked(agent,['/missing-unit-binary'],'test',root=t),127)
   self.assertEqual(field.run_tracked(agent,[sys.executable,'-c','raise SystemExit(9)'],'test',root=t),9)
   self.assertEqual(json.loads((Path(t)/'status'/f'{agent}.json').read_text())['state'],'failed')
 def test_artifact_owner_fence_and_secret_in_zip(self):
  agent=field.AGENTS[0]
  with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)),patch.dict(os.environ,{'GITHUB_TOKEN':'archive-test-secret'}):
   foreign=Path(t)/'foreign.zip';foreign.write_bytes(b'fake')
   with self.assertRaises(ValueError):release.own_file(agent,foreign)
   folder=Path(t)/'agents'/agent;folder.mkdir(parents=True);z=folder/'bundle.zip'
   with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED) as q:q.writestr('source.txt','archive-test-secret')
   with self.assertRaisesRegex(ValueError,'compressed'):release.own_file(agent,z)
if __name__=='__main__':unittest.main()
