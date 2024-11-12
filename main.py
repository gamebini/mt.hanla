import discord
from discord import app_commands
from datetime import datetime
from discord.ui import View, Button, Modal, TextInput, Select
import requests
import random
import asyncio
import os
from aiohttp import web
import threading

class BotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        
        print(f'Bot logged in as {self.user}')
        game = discord.Game('Made By Bini in Nexxa Interaction™')
        await self.change_presence(status=discord.Status.online, activity=game)

# 웹 서버 설정
async def handle(request):
    return web.Response(text="Bot is running!")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

class BotClient(discord.Client):
   def __init__(self):
       # 모든 인텐트 활성화
       super().__init__(intents=discord.Intents.all())
       self.synced = False
       
   async def on_ready(self):
       await self.wait_until_ready()
       if not self.synced:
           await tree.sync()
           self.synced = True
       
       print(f'Bot logged in as {self.user}')
       # 봇 상태 설정
       game = discord.Game('Made By Bini in Nexxa Interaction™')
       await self.change_presence(status=discord.Status.online, activity=game)

# 클라이언트 인스턴스 생성
client = BotClient()
tree = app_commands.CommandTree(client)

# 기본 에러 임베드 생성
error_embed = discord.Embed(
   title="ERROR", 
   description="해당 명령어를 사용할 수 있는 권한이 없습니다.",
   color=0xeb9534
)

def get_roblox_user_id(username):
    """로블록스 유저네임으로 유저 ID를 가져오는 함수"""
    url = f"https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username]}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        return data['data'][0]['id']
    else:
        return None

def get_user_description(user_id):
    """로블록스 유저 ID로 소개말을 가져오는 함수"""
    url = f"https://users.roblox.com/v1/users/{user_id}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('description', '')
    else:
        return None

def check_group_membership(user_id, group_id):
    """유저가 특정 그룹에 소속되어 있는지 확인하는 함수"""
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    response = requests.get(url)
    
    if response.status_code == 200:
        groups_data = response.json().get('data', [])
        return any(group['group']['id'] == group_id for group in groups_data)
    return False

class TicketDropdown(Select):
   def __init__(self):
       options = [
           discord.SelectOption(label="일반문의", description="일반적인 문의사항", emoji="❓"),
           discord.SelectOption(label="역할&명단 관련문의", description="역할 또는 명단과 관련된 문의사항", emoji="📝"),
           discord.SelectOption(label="인게임 & 디스코드 신고", description="신고 관련 문의사항", emoji="⚠️"),
           discord.SelectOption(label="양식 제출", description="각종 양식 제출", emoji="📨")
       ]
       super().__init__(placeholder="문의 종류를 선택해주세요", options=options)

   async def callback(self, interaction: discord.Interaction):
       ticket_type = self.values[0]
       await interaction.response.send_modal(TicketModal(ticket_type))

class CloseButton(Button):
   def __init__(self):
       super().__init__(style=discord.ButtonStyle.danger, label="티켓 닫기", emoji="🔒")

   async def callback(self, interaction: discord.Interaction):
       if not interaction.user.guild_permissions.manage_channels:
           embed = discord.Embed(title="ERROR", description="티켓을 닫을 권한이 없습니다.", color=0xeb9534)
           embed.set_footer(text="made by BINI in FICES™")
           await interaction.response.send_message(embed=embed, ephemeral=True)
           return

       # 티켓 생성자 ID 가져오기
       ticket_creator_id = int(interaction.channel.name.split("-")[-1])
       ticket_creator = interaction.guild.get_member(ticket_creator_id)

       # 티켓 생성자의 권한 제거
       await interaction.channel.set_permissions(ticket_creator, overwrite=None)

       # 닫힘 알림 임베드
       embed = discord.Embed(
           title="티켓이 닫혔습니다",
           description=f"관리자: {interaction.user.mention}",
           color=0xeb9534
       )
       embed.set_footer(text="made by BINI in FICES™")

       # 삭제 버튼이 포함된 뷰 생성
       view = View()
       view.add_item(DeleteButton())
       
       await interaction.response.send_message(embed=embed, view=view)

class DeleteButton(Button):
   def __init__(self):
       super().__init__(style=discord.ButtonStyle.danger, label="티켓 삭제", emoji="⛔")

   async def callback(self, interaction: discord.Interaction):
       if not interaction.user.guild_permissions.manage_channels:
           embed = discord.Embed(title="ERROR", description="티켓을 삭제할 권한이 없습니다.", color=0xeb9534)
           embed.set_footer(text="made by BINI in FICES™")
           await interaction.response.send_message(embed=embed, ephemeral=True)
           return

       # 삭제 전 알림
       embed = discord.Embed(
           title="티켓 삭제",
           description="이 티켓은 5초 후에 삭제됩니다.",
           color=0xeb9534
       )
       embed.set_footer(text="made by BINI in FICES™")
       await interaction.response.send_message(embed=embed)
       
       # 5초 대기 후 채널 삭제
       await asyncio.sleep(5)
       await interaction.channel.delete()

class TicketModal(Modal):
   def __init__(self, ticket_type: str):
       self.ticket_type = ticket_type
       super().__init__(title=f"{ticket_type}")
       
       self.content = TextInput(
           label="문의 내용",
           style=discord.TextStyle.long,
           placeholder="자세한 문의 내용을 입력해주세요...",
           required=True,
           max_length=4000
       )
       self.add_item(self.content)

   async def on_submit(self, interaction: discord.Interaction):
       prefix_map = {
           "일반문의": "일반",
           "역할&명단 관련문의": "역할명단",
           "인게임 & 디스코드 신고": "신고",
           "양식 제출": "양식"
       }
       
       prefix = prefix_map.get(self.ticket_type, "기타")
       
       category = interaction.guild.get_channel(1305890274068926515)
       channel_name = f"{prefix}-{interaction.user.id}"
       
       overwrites = {
           interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
           interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
           interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
       }
       
       for role in interaction.guild.roles:
           if role.permissions.administrator:
               overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
       
       ticket_channel = await interaction.guild.create_text_channel(
           name=channel_name,
           category=category,
           overwrites=overwrites
       )
       
       embed = discord.Embed(
           title="새로운 티켓이 생성되었습니다",
           description=f"문의자: {interaction.user.mention} ({interaction.user.id})\n"
                      f"문의 종류: {self.ticket_type}\n"
                      f"문의 내용:\n{self.content.value}",
           color=0xeb9534
       )
       embed.set_footer(text="made by BINI in FICES™")
       
       # 티켓 닫기 버튼이 포함된 뷰 생성
       view = View()
       view.add_item(CloseButton())
       
       await ticket_channel.send("@everyone", allowed_mentions=discord.AllowedMentions(everyone=True))
       await ticket_channel.send(embed=embed, view=view)
       
       confirmation_embed = discord.Embed(
           title="티켓 생성 완료",
           description=f"티켓이 생성되었습니다: {ticket_channel.mention}",
           color=0x55C098
       )
       confirmation_embed.set_footer(text="made by BINI in FICES™")
       await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)

class TicketView(View):
   def __init__(self):
       super().__init__(timeout=None)
       self.add_item(TicketDropdown())

@tree.command(name="티켓", description="새로운 티켓을 생성합니다.")
async def ticket(interaction: discord.Interaction):
   embed = discord.Embed(
       title="티켓 생성",
       description="아래 드롭다운 메뉴에서 문의 종류를 선택해주세요.",
       color=0xeb9534
   )
   embed.set_footer(text="made by BINI in FICES™")
   
   await interaction.response.send_message(
       embed=embed,
       view=TicketView(),
       ephemeral=True
   )

@tree.command(name="인증", description="로블록스 계정을 인증합니다.")
@app_commands.describe(로블록스닉네임='본인의 로블록스 닉네임을 입력하세요')
async def verify(interaction: discord.Interaction, 로블록스닉네임: str):
    # 초기 응답
    await interaction.response.defer(ephemeral=True)
    
    # 로블록스 유저 ID 가져오기
    user_id = get_roblox_user_id(로블록스닉네임)
    verified_role = interaction.guild.get_role(1304988824920657940)
    
    if not user_id:
        embed = discord.Embed(
            title="인증 실패",
            description="존재하지 않는 로블록스 계정입니다.",
            color=0xeb9534
        )
        embed.set_footer(text="made by BINI in Nexxa Interaction™")
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    # 임의의 인증 코드 생성
    verification_code = f"{random.randint(0, 999999):06d}"
    
    # 첫 번째 안내 메시지
    verify_embed = discord.Embed(
        title="인증 진행 중",
        description=f"로블록스 계정({로블록스닉네임})의 소개란에 아래 코드를 입력해주세요.\n**`{verification_code}`**\n입력 후 아래 버튼을 눌러주세요.",
        color=0xeb9534
    )
    verify_embed.set_footer(text="made by BINI in Nexxa Interaction™")

    # 버튼 생성
    verify_button = Button(label="입력 완료", style=discord.ButtonStyle.green)

    async def button_callback(button_interaction: discord.Interaction):
        # 버튼 누른 사람이 원래 명령어 사용자인지 확인
        if button_interaction.user.id != interaction.user.id:
            embed = discord.Embed(
                title="ERROR",
                description="본인의 인증 과정만 진행할 수 있습니다.",
                color=0xeb9534
            )
            embed.set_footer(text="made by BINI in Nexxa Interaction™")
            await button_interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 소개란 확인
        description = get_user_description(user_id)
        
        if not description or verification_code not in description:
            embed = discord.Embed(
                title="인증 실패",
                description="소개란에서 인증 코드를 찾을 수 없습니다.\n코드를 정확히 입력했는지 확인해주세요.",
                color=0xeb9534
            )
            embed.set_footer(text="made by BINI in Nexxa Interaction™")
            await button_interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 그룹 멤버십 확인
        if not check_group_membership(user_id, 17194017):
            embed = discord.Embed(
                title="인증 실패",
                description="댕댕이월드 그룹에 가입되어 있지 않습니다.\n그룹 가입 후 다시 시도해주세요.",
                color=0xeb9534
            )
            embed.set_footer(text="made by BINI in Nexxa Interaction™")
            await button_interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 모든 조건 충족 시 역할 지급
        try:
            await interaction.user.add_roles(verified_role) 
            await interaction.user.edit(nick=f"[ROKA] {로블록스닉네임}")
        except discord.Forbidden:
            embed = discord.Embed(
                title="ERROR",
                description="권한이 없습니다. 관리자에게 문의하세요.",
                color=0xeb9534
            )
            embed.set_footer(text="made by BINI in Nexxa Interaction™")
            await button_interaction.response.send_message(embed=embed, ephemeral=True)
            return
        except discord.HTTPException:
            embed = discord.Embed(
                title="ERROR",
                description="처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                color=0xeb9534
            )
            embed.set_footer(text="made by BINI in Nexxa Interaction™")
            await button_interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 성공 임베드 (채널)
        success_embed = discord.Embed(
            title="인증 완료",
            description=f"성공적으로 인증이 완료되었습니다.\n인증된 닉네임: {로블록스닉네임}",
            color=0x55C098
        )
        success_embed.set_footer(text="made by BINI in Nexxa Interaction™")
        await button_interaction.response.send_message(embed=success_embed, ephemeral=True)

        # DM 성공 메시지
        dm_embed = discord.Embed(
            title="인증 완료",
            description=f"한라산부대 디스코드 서버 인증이 완료되었습니다. 문의 명령어를 통해 역할을 받아주세요.\n인증된 닉네임: {로블록스닉네임}",
            color=0x55C098
        )
        dm_embed.set_footer(text="made by BINI in Nexxa Interaction™")
        try:
            await interaction.user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass  # DM 전송 실패 무시

    verify_button.callback = button_callback
    view = View()
    view.add_item(verify_button)
    await interaction.followup.send(embed=verify_embed, view=view, ephemeral=True)

# 기본 슬래시 커맨드 예시
@tree.command(name="ping", description="Checks the bot's latency")
async def ping(interaction: discord.Interaction):
   latency = round(client.latency * 1000)
   embed = discord.Embed(
       title="Pong!",
       description=f"Bot Latency: {latency}ms",
       color=0x55C098
   )
   await interaction.response.send_message(embed=embed)

# 멤버 입장 이벤트
@client.event
async def on_member_join(member):
   # 입장 메시지를 보낼 채널 ID 설정
   welcome_channel = client.get_channel(1287262605869846548)
   if welcome_channel:
       # 현재 시간 가져오기
       timestamp = datetime.now()
       
       embed = discord.Embed(
           title="WELCOME!",
           description=f"{member.mention}님이 서버에 입장하셨습니다! | {member.mention} has joined the server!",
           color=0x55C098,
           timestamp=timestamp
       )
       
       # 멤버의 프로필 사진을 썸네일로 설정
       embed.set_thumbnail(url=member.display_avatar.url)
       
       # 푸터 설정
       embed.set_footer(text="Made By Bini in Nexxa Interaction™")
       
       await welcome_channel.send(embed=embed)

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
   # 사용자가 음성 채널에서 나갔을 때
   if before.channel is not None:
       # 채널이 비었고, 채널 이름이 특정 형식일 때 삭제
       if len(before.channel.members) == 0:
           if before.channel.name.startswith("🔉ㅣ") or before.channel.name.startswith("🎵ㅣ"):
               await before.channel.delete()

   # 사용자가 새로운 음성 채널에 들어왔을 때
   if after.channel is not None:
       # 일반 음챗 생성
       if after.channel.id == 1305893668292395068:
           # 새 채널 생성
           new_channel = await member.guild.create_voice_channel(
               name=f"🔉ㅣ{member.display_name}의 음챗",
               category=after.channel.category,
               bitrate=after.channel.bitrate,
               user_limit=after.channel.user_limit
           )
           # 사용자를 새 채널로 이동
           await member.move_to(new_channel)

       # 음악 채널 생성
       elif after.channel.id == 1305894213317165087:
           # 새 채널 생성
           new_channel = await member.guild.create_voice_channel(
               name=f"🎵ㅣ{member.display_name}님의 음악채널",
               category=after.channel.category,
               bitrate=after.channel.bitrate,
               user_limit=after.channel.user_limit
           )
           # 사용자를 새 채널로 이동
           await member.move_to(new_channel)

# 봇 실행
if __name__ == "__main__":
    # 웹 서버와 봇을 함께 실행
    async def start():
        await run_web_server()
        TOKEN = os.environ['DISCORD_TOKEN']
        await client.start(TOKEN)

    # asyncio로 웹 서버와 봇을 함께 실행
    asyncio.run(start())
