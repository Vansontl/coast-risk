from __future__ import annotations
from typing import Dict, List

FACTOR_LABELS = {
    'X1': 'Điều kiện tự nhiên',
    'X2': 'Địa chất - nền móng',
    'X3': 'Kỹ thuật - công nghệ thi công',
    'X4': 'Vật liệu - thiết bị - logistics',
    'X5': 'Tổ chức - điều phối thi công',
    'X6': 'An toàn lao động - môi trường',
}


def _top_factors(inputs: Dict[str, float], limit: int = 2) -> List[tuple[str, float]]:
    items = [(k, float(v or 0)) for k, v in (inputs or {}).items() if k in FACTOR_LABELS]
    return sorted(items, key=lambda item: item[1], reverse=True)[:limit]


def _overall_actions(level: str) -> List[str]:
    mapping = {
        'Thấp': [
            'Duy trì tổ chức thi công theo kế hoạch hiện tại nhưng vẫn giữ cơ chế giám sát định kỳ theo ngày/ca.',
            'Tiếp tục cập nhật nhật ký hiện trường, điều kiện thủy hải văn và sai lệch thực tế để phát hiện sớm xu hướng tăng rủi ro.',
        ],
        'Trung bình': [
            'Thiết lập chế độ kiểm soát tăng cường đối với các hạng mục nhạy cảm, đặc biệt tại các thời điểm giao ca, chuyển bước thi công hoặc thay đổi điều kiện hiện trường.',
            'Rà soát trước các phương án dự phòng về nhân lực, thiết bị, vật tư và lịch thi công để tránh bị động khi rủi ro chuyển từ trung bình sang cao.',
        ],
        'Cao': [
            'Tổ chức họp điều hành kỹ thuật ngắn hạn để rà soát ngay biện pháp thi công, tiến độ, an toàn và khả năng đáp ứng nguồn lực trước khi triển khai tiếp các hạng mục chính.',
            'Áp dụng chế độ giám sát dày hơn theo ca/ngày, xác định rõ các điểm dừng kiểm tra bắt buộc trước khi cho phép tiếp tục thi công các công việc ngoài hiện trường.',
        ],
        'Rất cao': [
            'Ưu tiên đánh giá lại toàn bộ phương án thi công, đặc biệt các hạng mục ngoài biển hoặc nền móng nhạy cảm; chỉ tiếp tục khi các điều kiện kiểm soát rủi ro đã được xác nhận lại.',
            'Kích hoạt cơ chế chỉ huy tập trung giữa ban điều hành, tư vấn giám sát và các đội thi công để giảm nguy cơ ra quyết định phân tán trong điều kiện bất lợi.',
        ],
    }
    return mapping.get(level, [])


def _factor_actions(key: str, value: float) -> List[str]:
    if key == 'X1':
        return [
            f'Giá trị {key}={value:.2f} cho thấy cần siết theo dõi điều kiện thủy hải văn; nên cập nhật sóng, gió, triều và thời tiết theo khung thời gian ngắn hơn trước mỗi ca thi công.',
            'Ưu tiên điều chỉnh lịch thi công các công việc ngoài biển, công việc phụ thuộc thủy triều hoặc thiết bị nổi sang các cửa sổ thời tiết an toàn hơn.',
        ]
    if key == 'X2':
        return [
            f'Giá trị {key}={value:.2f} cho thấy rủi ro nền móng và địa chất cần được xem là trọng tâm; nên rà soát lại hồ sơ khảo sát, kiểm tra giả thiết đất yếu và các biện pháp xử lý nền hiện hành.',
            'Đối với các khu vực có dấu hiệu không đồng nhất nền đất, cần tăng mật độ kiểm tra hiện trường và bổ sung điểm kiểm soát lún, trượt hoặc xói cục bộ.',
        ]
    if key == 'X3':
        return [
            f'Giá trị {key}={value:.2f} gợi ý rủi ro kỹ thuật/công nghệ đang chi phối; cần rà soát biện pháp thi công chi tiết, trình tự thi công, khả năng đáp ứng của thiết bị và năng lực tổ đội kỹ thuật.',
            'Ưu tiên kiểm tra các điểm dễ phát sinh sai số thi công, sai lệch thiết kế, hoặc phụ thuộc quá lớn vào thao tác chuyên môn cao tại hiện trường.',
        ]
    if key == 'X4':
        return [
            f'Giá trị {key}={value:.2f} cho thấy cần tăng kiểm soát chuỗi cung ứng vật liệu, thiết bị và tuyến vận chuyển; nên rà soát trước khả năng chậm cấp vật tư hoặc nghẽn điều động thiết bị.',
            'Thiết lập phương án dự phòng logistics cho các vật tư/hạng mục then chốt để tránh dồn ép tiến độ và kéo theo rủi ro dây chuyền ở hiện trường.',
        ]
    if key == 'X5':
        return [
            f'Giá trị {key}={value:.2f} phản ánh rủi ro điều hành và phối hợp; cần củng cố cơ chế giao ban hiện trường, phân quyền xử lý tình huống và kiểm soát xung đột tiến độ giữa các mũi thi công.',
            'Nên rà lại mối nối giữa nhà thầu, tư vấn và chủ đầu tư để giảm rủi ro do chậm quyết định, chồng lấn trách nhiệm hoặc phản hồi không kịp thời.',
        ]
    if key == 'X6':
        return [
            f'Giá trị {key}={value:.2f} cho thấy cần coi an toàn lao động và môi trường là ưu tiên cấp thiết; nên kiểm tra lại phương án ứng cứu khẩn cấp, kiểm soát rủi ro ngoài biển và bảo vệ môi trường công trường.',
            'Bổ sung kiểm tra tuân thủ PPE, phân vùng nguy hiểm, cảnh báo hiện trường và khả năng sẵn sàng của lực lượng ứng cứu trong các ca thi công rủi ro cao.',
        ]
    return []


def _interaction_actions(top_keys: List[str]) -> List[str]:
    pair = tuple(top_keys[:2])
    pair_set = set(pair)
    actions = []
    if {'X1', 'X6'} <= pair_set:
        actions.append('Tổ hợp rủi ro tự nhiên và an toàn-môi trường đang nổi bật; nên coi đây là tình huống cần điều hành theo kịch bản phòng ngừa sự cố, không chỉ theo tiến độ đơn thuần.')
    if {'X2', 'X3'} <= pair_set:
        actions.append('Tổ hợp nền móng và kỹ thuật thi công cao cho thấy cần kiểm soát chặt sự phù hợp giữa điều kiện địa chất thực tế và biện pháp thi công đang áp dụng.')
    if {'X4', 'X5'} <= pair_set:
        actions.append('Tổ hợp logistics và điều phối cao cho thấy nguy cơ chậm tiến độ do tổ chức thi công; cần xử lý đồng thời cả nguồn lực lẫn cơ chế điều hành hiện trường.')
    if {'X1', 'X4'} <= pair_set:
        actions.append('Tổ hợp điều kiện tự nhiên và logistics cao cho thấy cần ưu tiên cửa sổ thi công an toàn gắn với kế hoạch cấp vật tư/thiết bị, tránh để hiện trường chờ nguồn lực trong điều kiện bất lợi.')
    return actions


def _stage_actions(stage: str | None) -> Dict[str, List[str]]:
    stage = (stage or '').strip().lower()
    if stage == 'chuẩn bị thi công':
        return {
            'immediate': ['Ưu tiên rà soát lại điều kiện sẵn sàng khởi công, đặc biệt là hồ sơ biện pháp, nguồn lực huy động ban đầu, mặt bằng thi công và cơ chế phối hợp giữa các bên trước khi tăng tốc triển khai.'],
            'priority': ['Tập trung kiểm tra độ đầy đủ của khảo sát, kế hoạch cung ứng vật tư - thiết bị và khả năng đáp ứng của bộ máy điều hành hiện trường ngay từ giai đoạn chuẩn bị để hạn chế rủi ro dồn tích về sau.'],
        }
    if stage == 'thi công nền móng':
        return {
            'immediate': ['Cần kiểm soát chặt sự phù hợp giữa điều kiện địa chất thực tế với biện pháp xử lý nền, đồng thời tăng giám sát các dấu hiệu lún, trượt, xói hoặc mất ổn định cục bộ trong suốt quá trình thi công nền móng.'],
            'priority': ['Mọi quyết định điều chỉnh kỹ thuật ở giai đoạn nền móng nên được xem xét như quyết định trọng yếu vì sai lệch ở giai đoạn này có thể lan truyền sang toàn bộ kết cấu và tiến độ công trình.'],
        }
    if stage == 'thi công thân đê/kè':
        return {
            'immediate': ['Ưu tiên điều phối đồng bộ giữa tiến độ thi công, điều kiện thời tiết - thủy hải văn và khả năng huy động vật tư/thiết bị để tránh phát sinh rủi ro dây chuyền trong giai đoạn thi công chính.'],
            'priority': ['Cần siết kiểm soát chất lượng vật liệu, cao độ, mái dốc, cấu kiện bảo vệ và an toàn ngoài hiện trường vì đây là giai đoạn dễ phát sinh áp lực tiến độ và sai lệch thi công.'],
        }
    if stage == 'hoàn thiện và bảo vệ':
        return {
            'immediate': ['Tăng cường kiểm tra chất lượng hoàn thiện, bảo vệ mái, cấu kiện bảo vệ và các hạng mục cuối kỳ; không để tâm lý gần kết thúc làm giảm mức độ kiểm soát rủi ro.'],
            'priority': ['Cần rà soát khả năng chống chịu của các hạng mục đã thi công trước khi bàn giao hoặc chuyển mùa, đặc biệt trong điều kiện công trình chịu tác động biển và thời tiết bất lợi.'],
        }
    return {'immediate': [], 'priority': []}


def _stakeholder_actions(level: str, dominant_label: str | None) -> Dict[str, List[str]]:
    dominant_text = dominant_label.lower() if dominant_label else 'nhóm rủi ro chi phối'
    return {
        'siteCommand': [
            f'Ban chỉ huy công trường cần tổ chức giao ban ngắn theo ca/ngày để cập nhật lại tình trạng {dominant_text}, chốt rõ điểm kiểm soát hiện trường và người chịu trách nhiệm xử lý.',
            'Các quyết định điều chỉnh biện pháp thi công, trình tự triển khai và huy động nguồn lực cần được truyền đạt thống nhất xuống từng mũi thi công để tránh lệch lệnh điều hành ngoài hiện trường.',
        ],
        'supervisionConsultant': [
            'Tư vấn giám sát nên tăng tần suất kiểm tra tại các điểm công việc nhạy cảm, đối chiếu thực tế với biện pháp đã phê duyệt và cảnh báo sớm các sai lệch có thể làm gia tăng rủi ro.',
            'Cần ghi nhận riêng các điểm không phù hợp về kỹ thuật, an toàn hoặc điều kiện hiện trường để làm cơ sở yêu cầu hiệu chỉnh biện pháp và tăng cường kiểm soát trước khi chuyển bước thi công.',
        ],
        'investorPMU': [
            'Chủ đầu tư/Ban QLDA nên tập trung vào các quyết định mang tính tháo gỡ điều kiện triển khai: phê duyệt điều chỉnh cần thiết, bảo đảm nguồn lực, và duy trì cơ chế phối hợp quyết định nhanh giữa các bên.',
            f'Đối với rủi ro đang nghiêng về {dominant_text}, cần ưu tiên chỉ đạo các cuộc họp điều hành có trọng tâm, tránh dàn trải và bảo đảm mọi điều chỉnh kỹ thuật/quản lý đều bám đúng mục tiêu kiểm soát rủi ro.',
        ],
    }


def build_risk_recommendations(inputs: Dict[str, float], score: float, level: str, project_stage: str | None = None, risk_matrix: Dict | None = None) -> Dict:
    tops = _top_factors(inputs, limit=2)
    dominant_key = tops[0][0] if tops else None
    dominant_label = FACTOR_LABELS.get(dominant_key) if dominant_key else None
    actions: List[str] = []
    actions.extend(_overall_actions(level))
    for key, value in tops:
        actions.extend(_factor_actions(key, value))
    actions.extend(_interaction_actions([key for key, _ in tops]))
    stage_actions = _stage_actions(project_stage)
    actions = stage_actions.get('immediate', []) + actions + stage_actions.get('priority', [])
    deduped = []
    seen = set()
    for item in actions:
        norm = item.strip()
        if norm and norm not in seen:
            seen.add(norm)
            deduped.append(norm)
    immediate_actions = deduped[:2]
    focused_actions = deduped[2:5]
    monitoring = [
        'Theo dõi lại các biến X1..X6 sau mỗi giai đoạn thi công chính hoặc khi điều kiện hiện trường thay đổi rõ rệt, bảo đảm việc cập nhật rủi ro bám sát diễn biến công trường.',
        'Cập nhật lại đánh giá rủi ro trước khi chuyển sang hạng mục mới, thay đổi biện pháp thi công hoặc tăng cường cường độ thi công để tránh ra quyết định dựa trên trạng thái đã lỗi thời.',
        'Lưu vết đầy đủ các quyết định điều hành, sự cố cận nguy, sai lệch hiện trường và biện pháp khắc phục nhằm phục vụ kiểm soát vòng lặp quản trị rủi ro ở các giai đoạn tiếp theo.',
    ]
    stage_text = (project_stage or 'chưa xác định').strip()
    summary = f'Kết quả dự báo cho thấy công trình đang ở mức rủi ro {level.lower()} với điểm {score:.4f}. Trong bối cảnh giai đoạn thi công <strong>{stage_text}</strong>, trọng tâm điều hành hiện trường nên ưu tiên kiểm soát nhóm {dominant_label.lower() if dominant_label else "rủi ro chi phối"}, đồng thời tổ chức các quyết định kỹ thuật và quản lý theo hướng phòng ngừa sớm, không để rủi ro lan sang tiến độ, chất lượng và an toàn thi công.'
    management_message = 'Khuyến nghị dưới đây cần được hiểu trong mối liên hệ trực tiếp với giai đoạn thi công hiện tại: cùng một mức rủi ro nhưng ở giai đoạn khác nhau thì ưu tiên điều hành, điểm dừng kiểm soát và mức độ cảnh giác tại hiện trường cũng cần khác nhau.'
    return {
        'projectStage': project_stage,
        'dominantFactor': dominant_key,
        'dominantLabel': dominant_label,
        'topFactors': [{'key': key, 'label': FACTOR_LABELS.get(key), 'value': value} for key, value in tops],
        'summary': summary,
        'managementMessage': management_message,
        'immediateActions': immediate_actions,
        'priorityActions': focused_actions,
        'monitoringActions': monitoring,
        'stakeholderActions': _stakeholder_actions(level, dominant_label),
        'riskMatrix': risk_matrix or {},
    }
