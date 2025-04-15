-- Lookup utility to map card IDs to rank and suit
function interpretCardID(id)
  if id < 0 or id > 51 then
    return "UnknownCard(" .. tostring(id) .. ")"
  end

  local suits = {"Clubs", "Diamonds", "Hearts", "Spades"}
  local ranks = {"Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"}

  local suit = suits[(id & 3) + 1]
  local rank = ranks[(id >> 2) + 1]

  return rank .. " of " .. suit
end

-- Base pointer to the main game memory region
local basePointerAddress = 0x100D01C
local base = readPointer(basePointerAddress)

if base == nil or base == 0 then
  print("Failed to read base game memory pointer. Ensure the process is attached and the game is active.")
  return
end

print(string.format("Game base memory located at: 0x%X", base))

-- Offsets (relative to base pointer)
local columnCountOffset = 0x64
local firstColumnPointerOffset = 0x6C
local cardArrayCountOffset = 0x1C
local cardArrayStartOffset = 0x24
local bytesPerCard = 12
local cardHeaderOffset = 0x0

-- Read number of piles
local pileCount = readInteger(base + columnCountOffset)
if pileCount == nil then
  print("Unable to determine number of card piles.")
  return
end
if pileCount > 13 then pileCount = 13 end -- Max allowed

print("Detected pile count: " .. tostring(pileCount))
print("Reading game state...\n")

-- Labels for piles
local pileLabels = {
  "Stock", "Waste",
  "Foundation 1", "Foundation 2", "Foundation 3", "Foundation 4",
  "Tableau 1", "Tableau 2", "Tableau 3", "Tableau 4",
  "Tableau 5", "Tableau 6", "Tableau 7"
}

-- Process each pile
for i = 0, pileCount - 1 do
  local label = pileLabels[i + 1] or ("Pile " .. tostring(i))
  print("[" .. label .. "]")

  local pointerOffset = firstColumnPointerOffset + i * 4
  local pileAddress = readPointer(base + pointerOffset)

  if pileAddress == nil then
    print("  Could not resolve pile pointer.")
  else
    local cardTotal = readInteger(pileAddress + cardArrayCountOffset)
    if cardTotal == nil or cardTotal == 0 then
      print("  No cards in this pile.")
    else
      for j = 0, cardTotal - 1 do
        local cardLocation = pileAddress + cardArrayStartOffset + j * bytesPerCard
        local cardHeader = readSmallInteger(cardLocation + cardHeaderOffset)

        if cardHeader == nil then
          print(string.format("  Failed to read card data at offset 0x%X", cardLocation))
        else
          local isFaceUp = (cardHeader & 0x8000) ~= 0
          local cardID = cardHeader & 0x7FFF
          local label = interpretCardID(cardID)
          local displayHex = string.format("0x%04X", cardHeader)

          print(string.format("  %s - %s (%s)", isFaceUp and "Face Up" or "Face Down", label, displayHex))
        end
      end
    end
  end

  print("")
end

print("Game state parsing complete.")