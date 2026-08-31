import "../../styles/Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__brand">
          <h3>StartOn</h3>
          <p>시작을 연결하고, 성공으로 이어주는 창업 파트너</p>
          <p className="footer__muted">AI 기반 창업 인사이트 및 맞춤형 컨설팅 서비스</p>
        </div>

        <div className="footer__col">
          <h4>PROJECT TEAM</h4>
          <p>김두용 · 천상우 · 정예원</p>
          <p className="footer__muted">Planning · UX/UI Design · Frontend · Backend · AI</p>
        </div>

        <div className="footer__col">
          <h4>DATA SOURCE</h4>
          <p>서울 열린데이터광장</p>
          <p className="footer__muted">서울시 공공데이터를 활용하여 분석 서비스를 구성했습니다.</p>
        </div>
      </div>

      <div className="container footer__notice">
        <p>본 사이트는 프로젝트 및 포트폴리오 목적으로 제작되었습니다.</p>
        <p>본 서비스에서 제공되는 분석 결과는 참고용이며 실제 창업 결과를 보장하지 않습니다.</p>
        <p className="footer__copyright">© 2026 StartOn. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
