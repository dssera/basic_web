import pytest

from contextlib import nullcontext as does_not_raise


@pytest.mark.usefixtures("empty_buildings", "fill_buildings")
class TestBuildingService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "latitude, longitude, r, result, expectation",
        [
            ("0", 0, 0, 0, pytest.raises(TypeError)),
            (0, 0, 0, 0, does_not_raise()),
        ]
    )
    async def test_get_by_coordinates(self,
                                      latitude: float,
                                      longitude: float,
                                      r: float,
                                      result: dict,
                                      expectation):  # result very complex data type
        # 1 positive case (and probably you need to expand test data)
        # cases for all exceptions
        #   wrong data types
        #   etc
        pass
        # какие экспешены в нем могут быть? (Тут ты вероятно пойдшь в дев и перепишешь сервисы+хендлеры)
        #

        # async with AsyncSessionLocal() as session:
        #     try:
        #         query = select(func.count(Building.id))
        #         result = await session.execute(query)
        #         count = result.scalar()
        #         assert count == 3
        #     finally:
        #         await session.close()
