from loguru import logger
import primp
import random
import asyncio

from src.model.frontrunner.instance import Frontrunner
from src.model.cex_withdrawal.instance import CexWithdraw
from src.model.testnet_bridge.instance import TestnetBridge
from src.model.memebridge.instance import Memebridge
from src.model.dusted.instance import Dusted
from src.model.aircraft.instance import Aircraft
from src.model.magiceden.instance import MagicEden
from src.model.monadking_mint.instance import Monadking
from src.model.demask_mint.instance import Demask
from src.model.lilchogstars_mint.instance import Lilchogstars
from src.model.kintsu.instance import Kintsu
from src.model.orbiter.instance import Orbiter
from src.model.accountable.instance import Accountable
from src.model.shmonad.instance import Shmonad
from src.model.gaszip.instance import Gaszip
from src.model.monadverse_mint.instance import MonadverseMint
from src.model.bima.instance import Bima
from src.model.owlto.instance import Owlto
from src.model.magma.instance import Magma
from src.model.apriori import Apriori
from src.model.monad_xyz.instance import MonadXYZ
from src.model.nad_domains.instance import NadDomains
from src.utils.client import create_client
from src.utils.config import Config
from src.model.help.stats import WalletStats


class Start:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        discord_token: str,
        twitter_token: str,
        email: str,
        config: Config,

    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.discord_token = discord_token
        self.twitter_token = twitter_token
        self.email = email
        self.config = config

        self.session: primp.AsyncClient | None = None

    async def initialize(self):
        try:
            self.session = await create_client(self.proxy)

            return True
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False

    async def flow(self):
        try:
            monad = MonadXYZ(
                self.account_index,
                self.proxy,
                self.private_key,
                self.discord_token,
                self.config,
                self.session,
            )

            if "farm_faucet" in self.config.FLOW.TASKS:
                await monad.faucet()
                return True

            # Заранее определяем все задачи
            planned_tasks = []
            task_plan_msg = []
            task_index = 1  # Initialize a single counter for all tasks

            for task_item in self.config.FLOW.TASKS:
                if isinstance(task_item, list):
                    # For tasks in square brackets [], randomly select one
                    selected_task = random.choice(task_item)
                    planned_tasks.append((task_index, selected_task, "random_choice"))
                    task_plan_msg.append(f"{task_index}. {selected_task}")
                    task_index += 1
                elif isinstance(task_item, tuple):
                    # For tasks in parentheses (), shuffle and execute all
                    shuffled_tasks = list(task_item)
                    random.shuffle(shuffled_tasks)

                    # Add each shuffled task individually to the plan
                    for subtask in shuffled_tasks:
                        planned_tasks.append((task_index, subtask, "shuffled_item"))
                        task_plan_msg.append(f"{task_index}. {subtask}")
                        task_index += 1
                else:
                    planned_tasks.append((task_index, task_item, "single"))
                    task_plan_msg.append(f"{task_index}. {task_item}")
                    task_index += 1

            # Выводим план выполнения одним сообщением
            logger.info(
                f"[{self.account_index}] Task execution plan: {' | '.join(task_plan_msg)}"
            )

            # Выполняем задачи по плану
            for i, task, task_type in planned_tasks:
                logger.info(f"[{self.account_index}] Executing task {i}: {task}")
                await self.execute_task(task, monad)
                await self.sleep(task)

            return True
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False

    async def execute_task(self, task, monad):
        """Execute a single task"""
        task = task.lower()

        if task == "faucet":
            await monad.faucet()

        if task == "swaps":
            await monad.swaps(type="swaps")

        elif task == "ambient":
            await monad.swaps(type="ambient")

        elif task == "bean":
            await monad.swaps(type="bean")

        elif task == "izumi":
            await monad.swaps(type="izumi")

        elif task == "collect_all_to_monad":
            await monad.swaps(type="collect_all_to_monad")

        elif task == "gaszip":
            gaszip = Gaszip(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
            )
            await gaszip.refuel()

        elif task == "memebridge":
            memebridge = Memebridge(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
            )
            await memebridge.refuel()

        elif task == "apriori":
            apriori = Apriori(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await apriori.execute()

        elif task == "magma":
            magma = Magma(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await magma.execute()

        elif task == "owlto":
            owlto = Owlto(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await owlto.deploy_contract()

        elif task == "bima":
            bima = Bima(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await bima.get_faucet_tokens()
            await self.sleep("bima_faucet")

            if self.config.BIMA.LEND:
                await bima.lend()

        elif task == "monadverse":
            monadverse_mint = MonadverseMint(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await monadverse_mint.mint()

        elif task == "shmonad":
            shmonad = Shmonad(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await shmonad.swaps()

        # elif task == "accountable":
        #     accountable = Accountable(
        #         self.account_index,
        #         self.proxy,
        #         self.private_key,
        #         self.config,
        #         self.session,
        #     )
        #     await accountable.mint()

        elif task == "orbiter":
            orbiter = Orbiter(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await orbiter.bridge()

        elif task == "testnet_bridge":
            testnet_bridge = TestnetBridge(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await testnet_bridge.execute()

        elif task == "logs":
            wallet_stats = WalletStats(self.config, self.proxy)
            await wallet_stats.get_wallet_stats(self.private_key, self.account_index)

        elif task == "nad_domains":
            nad_domains = NadDomains(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await nad_domains.register_random_domain()

        elif task == "kintsu":
            kintsu = Kintsu(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await kintsu.execute()

        elif task == "lilchogstars":
            lilchogstars = Lilchogstars(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await lilchogstars.mint()

        elif task == "demask":
            demask = Demask(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await demask.mint()

        elif task == "monadking":
            monadking = Monadking(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
            )
            await monadking.mint()

        elif task == "monadking_unlocked":
            monadking_unlocked = Monadking(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
            )
            await monadking_unlocked.mint_unlocked()

        elif task == "magiceden":
            magiceden = MagicEden(
                self.account_index,
                self.proxy,
                self.config,
                self.private_key,
                self.session,
            )
            await magiceden.mint()

        elif task == "aircraft":
            aircraft = Aircraft(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await aircraft.execute()

        elif task == "dusted":
            dusty = Dusted(
                self.account_index,
                self.proxy,
                self.private_key,
                self.twitter_token,
                self.config,
                self.session,
            )
            await dusty.execute()

        elif task == "frontrunner":
            frontrunner = Frontrunner(
                self.account_index,
                self.proxy,
                self.private_key,
                self.config,
                self.session,
            )
            await frontrunner.send_transaction()

        elif task == "cex_withdrawal":
            cex_withdrawal = CexWithdraw(
                self.account_index,
                self.private_key,
                self.config,
            )
            await cex_withdrawal.withdraw()

    async def sleep(self, task_name: str):
        """Делает рандомную паузу между действиями"""
        pause = random.randint(
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
        )
        logger.info(
            f"[{self.account_index}] Sleeping {pause} seconds after {task_name}"
        )
        await asyncio.sleep(pause)
