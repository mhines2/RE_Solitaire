-- Constants
local hMemAddress = 0x100D01C
local offsetToDeckPointers = 0x6C
local numberOfDecks = 13
local maxCardsPerDeck = 52

-- Card decoding helpers
local suits = {"Spades", "Hearts", "Clubs", "Diamonds"}
local ranks = {
  [1] = "A", [2] = "2", [3] = "3", [4] = "4", [5] = "5",
  [6] = "6", [7] = "7", [8] = "8", [9] = "9", [10] = "10",
  [11] = "J", [12] = "Q", [13] = "K"
}

-- Reads a capped list of cards from a deck
function readDeck(deckAddr)
  local cards = {}
  for index = 0, maxCardsPerDeck - 1 do
    local cardBytes = readSmallInteger(deckAddr + index * 2)
    if cardBytes == nil or cardBytes == 0 then break end

    local faceUp = (cardBytes & 0x8000) ~= 0
    local cardID = cardBytes & 0x7FFF

    local rankIndex = cardID & 0xF
    local suitIndex = ((cardID >> 4) & 0x3) + 1

    local rawHex = string.format("0x%04X", cardBytes)

    local rank = ranks[rankIndex]
    if rank == nil then
      rank = "?Rank(" .. tostring(rankIndex) .. ")"
    end

    local suit = suits[suitIndex]
    if suit == nil then
      suit = "?Suit(" .. tostring(suitIndex) .. ")"
    end

    local cardStr = (faceUp and "[UP] " or "[DOWN] ") .. rank .. " of " .. suit .. " (" .. rawHex .. ")"
    table.insert(cards, cardStr)
  end
  return cards
end

-- Main logic
local hMem = readInteger(hMemAddress)
if hMem == nil then
  print("❌ Failed to read hMem pointer!")
  return
end

local deckPointerArrayAddr = hMem + offsetToDeckPointers
print("🧠 Game Memory Address: " .. string.format("0x%X", hMem))
print("🃏 Deck Pointer Array at: " .. string.format("0x%X", deckPointerArrayAddr))
print("----------- 🃏 Game State 🃏 -----------")

local deckNames = {
  "Stock", "Waste",
  "Tableau 1", "Tableau 2", "Tableau 3", "Tableau 4",
  "Tableau 5", "Tableau 6", "Tableau 7",
  "Foundation 1", "Foundation 2", "Foundation 3", "Foundation 4"
}

for i = 0, numberOfDecks - 1 do
  local deckPtr = readInteger(deckPointerArrayAddr + i * 4)
  if deckPtr ~= nil then
    local cards = readDeck(deckPtr)
    print(deckNames[i + 1] .. ":")
    if #cards == 0 then
      print("  (empty)")
    else
      for _, c in ipairs(cards) do
        print("  " .. c)
      end
    end
  else
    print(deckNames[i + 1] .. ": (pointer not found)")
  end
end

print("----------------------------------------")