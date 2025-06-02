import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq # A* 알고리즘의 우선순위 큐에 사용
from collections import deque

# 한글 폰트 설정 (GA_Facility_Optimizer.py와 동일하게)
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# --- A* 경로 탐색 알고리즘 ---
def heuristic(a, b):
    """맨해튼 거리 휴리스틱 함수 (상하좌우 이동만 고려 시)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_nearest_free_space(obstacle_grid, target_point, factory_w, factory_h, max_search_radius=5):
    """
    주어진 점에서 가장 가까운 빈 공간을 BFS로 찾습니다.
    
    Args:
        obstacle_grid: 장애물 그리드 (0: 빈 공간, 1: 장애물)
        target_point: 대상 점 (x, y)
        factory_w: 공장 너비
        factory_h: 공장 높이
        max_search_radius: 최대 탐색 반경
    
    Returns:
        tuple: 가장 가까운 빈 공간의 좌표 (x, y), 찾지 못하면 None
    """
    if not (0 <= target_point[0] < factory_w and 0 <= target_point[1] < factory_h):
        return None
        
    # 이미 빈 공간이면 그대로 반환
    if obstacle_grid[target_point[0]][target_point[1]] == 0:
        return target_point
    
    # BFS로 가장 가까운 빈 공간 찾기
    queue = deque([target_point])
    visited = set([target_point])
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # 8방향
    
    current_radius = 0
    while queue and current_radius <= max_search_radius:
        level_size = len(queue)
        current_radius += 1
        
        for _ in range(level_size):
            x, y = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # 경계 확인
                if not (0 <= nx < factory_w and 0 <= ny < factory_h):
                    continue
                    
                if (nx, ny) in visited:
                    continue
                    
                visited.add((nx, ny))
                
                # 빈 공간을 찾았으면 반환
                if obstacle_grid[nx][ny] == 0:
                    return (nx, ny)
                    
                queue.append((nx, ny))
    
    return None

def find_machine_access_points(machine_pos_info, machine_def, obstacle_grid, factory_w, factory_h):
    """
    설비의 접근 가능한 지점들을 찾습니다.
    설비 주변의 빈 공간 중에서 설비와 인접한 지점들을 반환합니다.
    
    Args:
        machine_pos_info: 설비 위치 정보 {x, y, center_x, center_y}
        machine_def: 설비 정의 정보 {footprint, clearance, ...}
        obstacle_grid: 장애물 그리드
        factory_w: 공장 너비
        factory_h: 공장 높이
    
    Returns:
        list: 접근 가능한 지점들의 리스트 [(x, y), ...]
    """
    footprint_w, footprint_h = machine_def["footprint"]
    start_x, start_y = machine_pos_info["x"], machine_pos_info["y"]
    
    access_points = []
    
    # 설비 주변의 인접한 빈 공간들을 찾기
    # 설비의 4면 (상하좌우) 주변 체크
    
    # 상단 (y - 1)
    for x in range(start_x, start_x + footprint_w):
        y = start_y - 1
        if 0 <= x < factory_w and 0 <= y < factory_h and obstacle_grid[x][y] == 0:
            access_points.append((x, y))
    
    # 하단 (y + footprint_h)
    for x in range(start_x, start_x + footprint_w):
        y = start_y + footprint_h
        if 0 <= x < factory_w and 0 <= y < factory_h and obstacle_grid[x][y] == 0:
            access_points.append((x, y))
    
    # 좌측 (x - 1)
    for y in range(start_y, start_y + footprint_h):
        x = start_x - 1
        if 0 <= x < factory_w and 0 <= y < factory_h and obstacle_grid[x][y] == 0:
            access_points.append((x, y))
    
    # 우측 (x + footprint_w)
    for y in range(start_y, start_y + footprint_h):
        x = start_x + footprint_w
        if 0 <= x < factory_w and 0 <= y < factory_h and obstacle_grid[x][y] == 0:
            access_points.append((x, y))
    
    return access_points

def get_best_access_point(machine_pos_info, machine_def, obstacle_grid, factory_w, factory_h):
    """
    설비에 대한 최적의 접근 지점을 찾습니다.
    
    Returns:
        tuple: 최적 접근 지점 (x, y)
    """
    # 먼저 설비 중심점이 빈 공간인지 확인
    center_x = int(round(machine_pos_info["center_x"]))
    center_y = int(round(machine_pos_info["center_y"]))
    
    if (0 <= center_x < factory_w and 0 <= center_y < factory_h and 
        obstacle_grid[center_x][center_y] == 0):
        return (center_x, center_y)
    
    # 설비 주변의 접근 가능한 지점들 찾기
    access_points = find_machine_access_points(machine_pos_info, machine_def, obstacle_grid, factory_w, factory_h)
    
    if access_points:
        # 중심점에서 가장 가까운 접근 지점 선택
        center_point = (machine_pos_info["center_x"], machine_pos_info["center_y"])
        best_point = min(access_points, 
                        key=lambda p: abs(p[0] - center_point[0]) + abs(p[1] - center_point[1]))
        return best_point
    
    # 접근 지점이 없으면 BFS로 가장 가까운 빈 공간 찾기
    fallback_point = find_nearest_free_space(obstacle_grid, (center_x, center_y), 
                                           factory_w, factory_h, max_search_radius=10)
    
    if fallback_point:
        return fallback_point
    
    # 마지막 수단: 원래 중심점 반환 (경로 탐색이 실패할 수 있음)
    print(f"경고: 설비 주변에서 접근 가능한 지점을 찾지 못했습니다. 중심점을 사용합니다: ({center_x}, {center_y})")
    return (center_x, center_y)

def get_optimized_access_point_for_sequence(prev_access_point, current_pos_info, current_machine_def, 
                                          next_pos_info, next_machine_def, obstacle_grid, factory_w, factory_h):
    """
    연속된 3개 설비의 경로를 고려하여 중간 설비의 최적 접근 지점을 찾습니다.
    
    Args:
        prev_access_point: 이전 설비의 접근 지점 (x, y)
        current_pos_info: 현재 설비 위치 정보
        current_machine_def: 현재 설비 정의 정보
        next_pos_info: 다음 설비 위치 정보  
        next_machine_def: 다음 설비 정의 정보
        obstacle_grid: 장애물 그리드
        factory_w: 공장 너비
        factory_h: 공장 높이
    
    Returns:
        tuple: 최적 접근 지점 (x, y)
    """
    # 현재 설비의 모든 접근 가능한 지점들 구하기
    current_access_points = find_machine_access_points(current_pos_info, current_machine_def, 
                                                     obstacle_grid, factory_w, factory_h)
    
    # 접근 지점이 없으면 기존 방식 사용
    if not current_access_points:
        return get_best_access_point(current_pos_info, current_machine_def, obstacle_grid, factory_w, factory_h)
    
    # 다음 설비의 접근 가능한 지점들도 구하기 (가장 가까운 것 사용)
    next_access_points = find_machine_access_points(next_pos_info, next_machine_def, 
                                                  obstacle_grid, factory_w, factory_h)
    
    # 다음 설비 접근점이 없으면 중심점 사용
    if not next_access_points:
        next_target = get_best_access_point(next_pos_info, next_machine_def, obstacle_grid, factory_w, factory_h)
    else:
        # 다음 설비의 중심점에서 가장 가까운 접근점 선택
        next_center = (next_pos_info["center_x"], next_pos_info["center_y"])
        next_target = min(next_access_points, 
                         key=lambda p: abs(p[0] - next_center[0]) + abs(p[1] - next_center[1]))
    
    # 각 현재 설비 접근점에 대해 전체 경로 길이 계산
    best_point = None
    min_total_distance = float('inf')
    
    for current_point in current_access_points:
        # 이전 → 현재 거리 (맨해튼 거리)
        dist_prev_to_current = abs(prev_access_point[0] - current_point[0]) + abs(prev_access_point[1] - current_point[1])
        
        # 현재 → 다음 거리 (맨해튼 거리) 
        dist_current_to_next = abs(current_point[0] - next_target[0]) + abs(current_point[1] - next_target[1])
        
        # 전체 거리
        total_distance = dist_prev_to_current + dist_current_to_next
        
        if total_distance < min_total_distance:
            min_total_distance = total_distance
            best_point = current_point
    
    # 최적점을 찾지 못한 경우 기존 방식 사용
    if best_point is None:
        return get_best_access_point(current_pos_info, current_machine_def, obstacle_grid, factory_w, factory_h)
    
    return best_point

def a_star_search(grid_map, start_coords, goal_coords, factory_w, factory_h):
    """
    A* 알고리즘으로 그리드 맵에서 시작점에서 목표점까지의 경로를 찾습니다.
    grid_map[x][y] == 1 이면 장애물, 0 이면 통행 가능.
    """
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)] # 상하좌우 이동
    # 대각선 이동 추가 시: neighbors += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    close_set = set()
    came_from = {}
    gscore = {start_coords: 0}
    fscore = {start_coords: heuristic(start_coords, goal_coords)}
    oheap = [] # 우선순위 큐

    heapq.heappush(oheap, (fscore[start_coords], start_coords))
    
    while oheap:
        current_fscore, current_node = heapq.heappop(oheap)

        if current_node == goal_coords:
            path_data = []
            while current_node in came_from:
                path_data.append(current_node)
                current_node = came_from[current_node]
            path_data.append(start_coords) # 시작점 추가
            return path_data[::-1] # 경로 뒤집기

        close_set.add(current_node)
        for i, j in neighbors:
            neighbor = current_node[0] + i, current_node[1] + j
            
            # 그리드 범위 및 장애물 확인
            if not (0 <= neighbor[0] < factory_w and 0 <= neighbor[1] < factory_h):
                continue
            if grid_map[neighbor[0]][neighbor[1]] == 1: # 장애물인 경우
                continue
                
            tentative_g_score = gscore[current_node] + 1 # 이동 비용은 1로 가정

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                continue
                
            if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [item[1] for item in oheap]:
                came_from[neighbor] = current_node
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal_coords)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
                
    return None # 경로를 찾지 못한 경우

# --- 레이아웃 및 경로 시각화 함수 ---
def visualize_layout_with_paths(layout_data, all_paths, filename="layout_with_paths.png"):
    factory_w = layout_data["factory_width"]
    factory_h = layout_data["factory_height"]
    machine_positions_map = layout_data["machine_positions_map"]
    process_sequence_list = layout_data["process_sequence"]
    machine_definitions_list = layout_data["machines_definitions"]

    fig, ax = plt.subplots(1, figsize=(factory_w/2.5, factory_h/2.8)) # 그림 크기 조절
    ax.set_xlim(-0.5, factory_w - 0.5)
    ax.set_ylim(-0.5, factory_h - 0.5)
    ax.set_xticks(range(factory_w))
    ax.set_yticks(range(factory_h))
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_aspect('equal', adjustable='box')

    num_total_machines_for_color = len(machine_definitions_list)
    cmap_machines = plt.colormaps.get_cmap('viridis')
    machines_dict_by_id = {m['id']: m for m in machine_definitions_list}

    # 설비 그리기
    for machine_id_str, pos_data in machine_positions_map.items(): # JSON 로드 시 key가 str일 수 있음
        machine_id = int(machine_id_str) # int로 변환
        machine_info = machines_dict_by_id.get(machine_id)
        if machine_info:
            x, y = pos_data['x'], pos_data['y']
            width, height = machine_info['footprint']
            clearance = machine_info.get('clearance', 0)
            
            normalized_id = machine_id / max(num_total_machines_for_color - 1, 1)
            face_color = cmap_machines(normalized_id)

            rect_body = patches.Rectangle((x - 0.5, y - 0.5), width, height,
                                          linewidth=1.5, edgecolor='black',
                                          facecolor=face_color, alpha=0.7)
            ax.add_patch(rect_body)
            ax.text(x + width/2 - 0.5, y + height/2 - 0.5, f"M{machine_id}",
                    ha='center', va='center', fontsize=7, color='white', weight='bold')
            if clearance > 0:
                rect_clearance = patches.Rectangle(
                    (x - clearance - 0.5, y - clearance - 0.5),
                    width + 2*clearance, height + 2*clearance,
                    linewidth=1, edgecolor=face_color, facecolor='none', linestyle=':', alpha=0.3)
                ax.add_patch(rect_clearance)

    # 경로 그리기
    cmap_paths = plt.colormaps.get_cmap('cool') # 경로를 위한 다른 컬러맵
    num_paths = len(all_paths)
    path_number = 1
    labels_at_start_node = {}
    for i, path_segment in enumerate(all_paths):
        if path_segment:
            path_color = cmap_paths(i / max(num_paths - 1, 1))
            path_xs = [p[0] for p in path_segment]
            path_ys = [p[1] for p in path_segment]
            ax.plot(path_xs, path_ys, color=path_color, linewidth=2, alpha=0.8, marker='o', markersize=3)
            # 경로 시작점에 번호 표시 (선택적)
            if len(path_segment) > 0:
                start_node_tuple = tuple(path_segment[0]) # 시작점 좌표 (튜플이어야 딕셔너리 키로 사용 가능)

                # 이 시작점에서 이전에 몇 개의 라벨이 그려졌는지 확인
                offset_idx = labels_at_start_node.get(start_node_tuple, 0)

                # 라벨 y 위치 조정: 각 라벨을 이전 라벨보다 조금 더 위로 (Y축이 반전되어 있으므로 작은 값이 더 위)
                # 0.4는 예시 값이며, 폰트 크기나 원하는 간격에 따라 조절 필요
                adjusted_y_pos = path_segment[0][1] - 0.3 - (offset_idx * 1)
                adjusted_x_pos = path_segment[0][0] # x 위치는 그대로 두거나, 필요시 함께 조정

                ax.text(adjusted_x_pos, adjusted_y_pos, f"{path_number}",
                        color=path_color,
                        fontsize=10,
                        weight='bold',
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray', pad=0.2, boxstyle='round'))

                # 이 시작점의 라벨 카운트 업데이트
                labels_at_start_node[start_node_tuple] = offset_idx + 1
                path_number += 1

    plt.title("Factory Layout with Optimized Continuous Paths", fontsize=14)
    plt.xlabel("Factory Width (X)")
    plt.ylabel("Factory Height (Y)")
    plt.gca().invert_yaxis() # Y축을 위에서 아래로 증가

    try:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 연속 경로 최적화 레이아웃 시각화 이미지 저장 완료: {filename}")
    except Exception as e:
        print(f"경로 시각화 이미지 저장 중 오류 발생: {e}")
    plt.show() # 화면에도 표시
    plt.close(fig)


# --- 메인 실행 함수 ---
def main_path_finder(layout_data_file="optimized_layout_data.json"):
    # 1. 레이아웃 데이터 로드
    try:
        with open(layout_data_file, "r", encoding="utf-8") as f:
            layout_data = json.load(f)
    except FileNotFoundError:
        print(f"오류: 레이아웃 데이터 파일 '{layout_data_file}'을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        print(f"오류: 레이아웃 데이터 파일 '{layout_data_file}'의 형식이 잘못되었습니다.")
        return

    factory_w = layout_data["factory_width"]
    factory_h = layout_data["factory_height"]
    machine_positions = layout_data["machine_positions_map"] # {id_str: {x,y,center_x,center_y}}
    process_sequence = layout_data["process_sequence"]
    machines_definitions = layout_data["machines_definitions"]
    machines_dict = {m['id']: m for m in machines_definitions}


    # 2. 경로 탐색을 위한 그리드 맵 생성 (장애물 표시)
    # 0: 이동 가능, 1: 장애물 (설비 몸체)
    obstacle_grid = [[0 for _ in range(factory_h)] for _ in range(factory_w)]
    for machine_id_str, pos_info in machine_positions.items():
        machine_id = int(machine_id_str)
        m_def = machines_dict.get(machine_id)
        if m_def:
            footprint_w, footprint_h = m_def["footprint"]
            start_x, start_y = pos_info["x"], pos_info["y"]
            for i in range(start_x, start_x + footprint_w):
                for j in range(start_y, start_y + footprint_h):
                    if 0 <= i < factory_w and 0 <= j < factory_h:
                        obstacle_grid[i][j] = 1 # 설비 몸체는 장애물

    # 3. 연속 경로 최적화를 고려한 경로 탐색 
    print("🚀 한붓그리기식 연속 경로 최적화 시작...")
    all_paths_found = []
    access_points_cache = {}  # 설비별 최적 접근점 캐시
    
    # 첫 번째 설비의 접근점 미리 계산 (기존 방식)
    first_machine_id = process_sequence[0]
    first_pos_info = machine_positions.get(str(first_machine_id))
    first_machine_def = machines_dict.get(first_machine_id)
    if first_pos_info and first_machine_def:
        access_points_cache[first_machine_id] = get_best_access_point(
            first_pos_info, first_machine_def, obstacle_grid, factory_w, factory_h)
    
    for i in range(len(process_sequence) - 1):
        current_machine_id = process_sequence[i]
        next_machine_id = process_sequence[i+1]

        # machine_positions의 key가 문자열일 수 있으므로 str()로 변환하여 조회
        current_pos_info = machine_positions.get(str(current_machine_id))
        next_pos_info = machine_positions.get(str(next_machine_id))

        if not current_pos_info or not next_pos_info:
            print(f"경고: 설비 ID {current_machine_id} 또는 {next_machine_id}의 위치 정보를 찾을 수 없습니다.")
            all_paths_found.append(None) # 해당 구간 경로 없음
            continue

        # 현재 설비와 다음 설비의 정의 정보 가져오기
        current_machine_def = machines_dict.get(current_machine_id)
        next_machine_def = machines_dict.get(next_machine_id)

        if not current_machine_def or not next_machine_def:
            print(f"경고: 설비 ID {current_machine_id} 또는 {next_machine_id}의 정의 정보를 찾을 수 없습니다.")
            all_paths_found.append(None)
            continue

        # 시작점 결정 (이미 캐시에 있으면 사용)
        if current_machine_id in access_points_cache:
            start_node = access_points_cache[current_machine_id]
        else:
            start_node = get_best_access_point(current_pos_info, current_machine_def, 
                                             obstacle_grid, factory_w, factory_h)
            access_points_cache[current_machine_id] = start_node

        # 목표점 결정 - 연속 경로 최적화 적용
        if i < len(process_sequence) - 2:  # 중간 설비인 경우 (다음 다음 설비가 존재)
            # 다음 다음 설비 정보 가져오기
            next_next_machine_id = process_sequence[i+2]
            next_next_pos_info = machine_positions.get(str(next_next_machine_id))
            next_next_machine_def = machines_dict.get(next_next_machine_id)
            
            if next_next_pos_info and next_next_machine_def:
                # 연속 경로 최적화 적용
                goal_node = get_optimized_access_point_for_sequence(
                    start_node, next_pos_info, next_machine_def,
                    next_next_pos_info, next_next_machine_def,
                    obstacle_grid, factory_w, factory_h)
                access_points_cache[next_machine_id] = goal_node
                print(f"🎯 연속 최적화 적용: 설비 {current_machine_id} → {next_machine_id} → {next_next_machine_id}")
            else:
                # 다음 다음 설비 정보가 없으면 기존 방식
                goal_node = get_best_access_point(next_pos_info, next_machine_def, 
                                                obstacle_grid, factory_w, factory_h)
                access_points_cache[next_machine_id] = goal_node
        else:
            # 마지막 구간인 경우 기존 방식
            goal_node = get_best_access_point(next_pos_info, next_machine_def, 
                                            obstacle_grid, factory_w, factory_h)
            access_points_cache[next_machine_id] = goal_node

        print(f"경로 탐색 중: 설비 {current_machine_id} ({start_node}) -> 설비 {next_machine_id} ({goal_node})")
        
        # 시작점과 목표점이 동일한 경우 처리
        if start_node == goal_node:
            print(f"  시작점과 목표점이 동일합니다. 직접 연결.")
            all_paths_found.append([start_node, goal_node])
            continue
            
        path = a_star_search(obstacle_grid, start_node, goal_node, factory_w, factory_h)
        
        if path:
            print(f"  경로 발견: {len(path)} 단계")
            all_paths_found.append(path)
        else:
            print(f"  경로를 찾지 못했습니다.")
            # 경로를 찾지 못한 경우에도 직선으로 표시 (시각화용)
            all_paths_found.append([start_node, goal_node])
            
    # 4. 연속 경로 최적화 레이아웃과 함께 경로 시각화
    print("🎨 한붓그리기 최적화 결과 시각화 중...")
    visualize_layout_with_paths(layout_data, all_paths_found)


if __name__ == "__main__":
    main_path_finder()
