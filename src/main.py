import pygame
import numpy as np
import random

# 初始化Pygame
pygame.init()
pygame.font.init()

# 设置窗口大小和标题
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
PLOT_AREA_WIDTH = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("K-means算法演示")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (230, 240, 255)  # 淡蓝色用于按钮悬停
BUTTON_BLUE = (70, 120, 255)  # 按钮文字颜色
INPUT_BG = (240, 240, 240)  # 输入框背景色
COLORS = [
    (255, 0, 0),  # 红
    (0, 255, 0),  # 绿
    (0, 0, 255),  # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
    (0, 255, 255),  # 青
    (128, 0, 0),  # 深红
    (0, 128, 0),  # 深绿
    (0, 0, 128),  # 深蓝
]

# 字体设置
# 尝试加载中文字体，按优先级尝试不同字体
try:
    FONT = pygame.font.SysFont("microsoftyahei", 24)  # 微软雅黑
except:
    try:
        FONT = pygame.font.SysFont("simhei", 24)  # 黑体
    except:
        try:
            FONT = pygame.font.SysFont("simsun", 24)  # 宋体
        except:
            FONT = pygame.font.SysFont(None, 24)  # 如果都失败了，使用默认字体


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        # 添加圆角矩形的半径
        self.border_radius = 10

    def draw(self, surface):
        # 绘制圆角矩形背景
        color = LIGHT_BLUE if self.is_hovered else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        # 绘制边框
        pygame.draw.rect(
            surface, BUTTON_BLUE, self.rect, 2, border_radius=self.border_radius
        )

        # 绘制文字，使用蓝色
        text_surface = FONT.render(self.text, True, BUTTON_BLUE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class InputBox:
    def __init__(self, x, y, width, height, text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.active = False
        self.label = ""
        # 添加圆角矩形的半径
        self.border_radius = 8

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode

    def draw(self, surface):
        # 绘制输入框背景
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=self.border_radius)

        # 绘制边框，激活时使用蓝色
        border_color = BUTTON_BLUE if self.active else GRAY
        pygame.draw.rect(
            surface, border_color, self.rect, 2, border_radius=self.border_radius
        )

        # 绘制文本
        text_surface = FONT.render(self.text, True, BLACK)
        width = max(self.rect.w, text_surface.get_width() + 10)
        # 调整文本位置，使其垂直居中
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (self.rect.x + 8, text_y))

        if self.label:
            # 标签使用蓝色
            label_surface = FONT.render(self.label, True, BUTTON_BLUE)
            surface.blit(label_surface, (self.rect.x, self.rect.y - 30))


def initialize_points(n_points, k):
    """初始化数据点和中心点"""
    global points, centroids, point_labels

    # 设置K个基准中心点，将点分散在这些中心点周围
    base_centers = [
        (200, 200),  # 左上
        (200, 400),  # 左下
        (400, 300),  # 右中
        (400, 150),  # 右上
        (400, 450),  # 右下
        (300, 300),  # 中心
        (150, 300),  # 左中
        (350, 200),  # 中上
        (350, 400),  # 中下
    ]

    # 确保基准点数量足够
    while len(base_centers) < k:
        base_centers.append(
            (
                random.randint(150, PLOT_AREA_WIDTH - 150),
                random.randint(150, WINDOW_HEIGHT - 150),
            )
        )

    # 生成围绕基准中心的随机点
    points = []
    points_per_cluster = n_points // k
    remaining_points = n_points % k

    for i in range(k):
        center = base_centers[i]
        # 为每个簇生成点
        for _ in range(points_per_cluster + (1 if i < remaining_points else 0)):
            # 在基准中心周围生成随机偏移
            offset_x = random.gauss(0, 50)  # 使用高斯分布生成偏移
            offset_y = random.gauss(0, 50)

            # 确保点在有效范围内
            x = min(max(50, int(center[0] + offset_x)), PLOT_AREA_WIDTH - 50)
            y = min(max(50, int(center[1] + offset_y)), WINDOW_HEIGHT - 50)

            points.append((x, y))

    # 随机打乱点的顺序
    random.shuffle(points)

    # 随机选择K个中心点
    centroids = random.sample(points, k)

    # 初始化标签为-1（未分配）
    point_labels = [-1] * len(points)


def calculate_distance(p1, p2):
    """计算两点之间的欧几里得距离"""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def assign_points():
    """将每个点分配到最近的簇"""
    global point_labels

    for i, point in enumerate(points):
        min_dist = float("inf")
        closest_centroid = 0

        for j, centroid in enumerate(centroids):
            dist = calculate_distance(point, centroid)
            if dist < min_dist:
                min_dist = dist
                closest_centroid = j

        point_labels[i] = closest_centroid


def update_centroids():
    """更新每个簇的中心点"""
    global centroids

    for i in range(len(centroids)):
        cluster_points = [p for j, p in enumerate(points) if point_labels[j] == i]
        if cluster_points:
            # 计算簇中所有点的平均位置
            x_mean = sum(p[0] for p in cluster_points) / len(cluster_points)
            y_mean = sum(p[1] for p in cluster_points) / len(cluster_points)
            centroids[i] = (int(x_mean), int(y_mean))


def draw_points():
    """绘制所有点和中心点"""
    # 绘制普通点
    for i, point in enumerate(points):
        color = COLORS[point_labels[i]] if point_labels[i] != -1 else BLACK
        pygame.draw.circle(window, color, point, 4)

    # 绘制中心点（用大一点的圆和黑色边框表示）
    for i, centroid in enumerate(centroids):
        pygame.draw.circle(window, WHITE, centroid, 8)
        pygame.draw.circle(window, COLORS[i], centroid, 7)
        pygame.draw.circle(window, BLACK, centroid, 8, 1)


# 游戏状态
points = []  # 所有数据点
centroids = []  # 簇中心点
point_labels = []  # 每个点属于哪个簇
n_points = 100  # 初始点数量
k_clusters = 3  # 分类簇数量

# 创建UI元素
PANEL_LEFT = 650  # 右侧面板起始x坐标
PANEL_WIDTH = 300  # 右侧面板宽度
INPUT_WIDTH = 120  # 输入框宽度
BUTTON_WIDTH = 240  # 按钮宽度
ELEMENT_HEIGHT = 36  # 元素高度

# 创建输入框
input_n_points = InputBox(
    PANEL_LEFT + (PANEL_WIDTH - INPUT_WIDTH) // 2,
    50,
    INPUT_WIDTH,
    ELEMENT_HEIGHT,
    str(n_points),
)
input_n_points.label = "初始点数量"
input_k_clusters = InputBox(
    PANEL_LEFT + (PANEL_WIDTH - INPUT_WIDTH) // 2,
    130,
    INPUT_WIDTH,
    ELEMENT_HEIGHT,
    str(k_clusters),
)
input_k_clusters.label = "分类簇数量K"

# 创建按钮
btn_init = Button(
    PANEL_LEFT + (PANEL_WIDTH - BUTTON_WIDTH) // 2,
    290,
    BUTTON_WIDTH,
    ELEMENT_HEIGHT,
    "初始化",
)
btn_assign = Button(
    PANEL_LEFT + (PANEL_WIDTH - BUTTON_WIDTH) // 2,
    350,
    BUTTON_WIDTH,
    ELEMENT_HEIGHT,
    "分配样本到簇",
)
btn_update = Button(
    PANEL_LEFT + (PANEL_WIDTH - BUTTON_WIDTH) // 2,
    410,
    BUTTON_WIDTH,
    ELEMENT_HEIGHT,
    "更新簇中心点",
)

input_boxes = [input_n_points, input_k_clusters]
buttons = [btn_init, btn_assign, btn_update]

# 主游戏循环
running = True
while running:
    window.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 处理输入框事件
        for box in input_boxes:
            box.handle_event(event)

        # 处理按钮事件
        for button in buttons:
            if button.handle_event(event):
                if button == btn_init:
                    try:
                        n_points = int(input_n_points.text)
                        k_clusters = int(input_k_clusters.text)
                        initialize_points(n_points, k_clusters)
                    except ValueError:
                        pass  # 忽略无效的输入值
                elif button == btn_assign:
                    assign_points()
                elif button == btn_update:
                    update_centroids()

    # 绘制分隔线
    pygame.draw.line(
        window, BLACK, (PLOT_AREA_WIDTH, 0), (PLOT_AREA_WIDTH, WINDOW_HEIGHT)
    )

    # 绘制UI元素
    for box in input_boxes:
        box.draw(window)
    for button in buttons:
        button.draw(window)

    # 如果有点要绘制，就绘制它们
    if points:
        draw_points()

    pygame.display.flip()

pygame.quit()
