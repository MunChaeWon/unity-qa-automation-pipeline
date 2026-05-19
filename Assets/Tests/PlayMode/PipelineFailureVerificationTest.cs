using System.Collections;
using NUnit.Framework;
using UnityEngine.TestTools;

public class PipelineFailureVerificationTest
{
    // 실패 검증을 끄고 싶으면 아래 Ignore를 활성화함
    // 실패 검증을 하고 싶으면 아래 Ignore를 주석 처리함
    //[Ignore("파이프라인 실패 처리 검증이 필요할 때만 Ignore를 제거함")]
    [UnityTest]
    public IEnumerator TC_FAIL_999_PipelineFailureVerification()
    {
        yield return null;

        Assert.Fail("Jira Bug 및 Allure 실패 리포트 생성 확인을 위한 의도적 실패 테스트");
    }
}