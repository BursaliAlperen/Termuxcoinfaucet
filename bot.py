-- ╔══════════════════════════════════════════════════════════════════╗
-- ║     AUT ULTIMATE COMBAT  ·  OMEGA PRO v2.0 FINAL               ║
-- ║   UI GARANTİLİ  | GÖRÜNÜRLÜK KESİN  | STABİL                   ║
-- ╚══════════════════════════════════════════════════════════════════╝

-- ══════════════════════════════════════════════════════════════════
-- SERVİSLER & REFERANSLAR
-- ══════════════════════════════════════════════════════════════════
local Players            = game:GetService("Players")
local TweenService       = game:GetService("TweenService")
local RunService         = game:GetService("RunService")
local VIM                = game:GetService("VirtualInputManager")
local Workspace          = game:GetService("Workspace")
local Camera             = Workspace.CurrentCamera
local UserInputService   = game:GetService("UserInputService")
local HttpService        = game:GetService("HttpService")
local Debris             = game:GetService("Debris")

local player             = Players.LocalPlayer
local character          = player.Character or player.CharacterAdded:Wait()
local humanoid           = character:WaitForChild("Humanoid")
local rootPart           = character:WaitForChild("HumanoidRootPart")

-- ══════════════════════════════════════════════════════════════════
-- PROFESYONEL KONFİGÜRASYON
-- ══════════════════════════════════════════════════════════════════
local CFG = {
    -- Hedef Sistemi
    TargetPlayers       = true,
    TargetNPCs          = true,
    TargetAllies        = false,
    MaxRange            = 300,
    FOV_Angle           = 180,
    SmartSearch         = true,
    TargetPriority      = "Distance",  -- "Distance", "LowHP", "Threat"
    TargetBlacklist     = {},
    MinTargetHealth     = 0,
    RetargetDelay       = 0.3,

    -- Savaş Mesafeleri (studs)
    KillAuraRange       = 4.5,
    UltraClose          = 5,
    CloseRange          = 14,
    MidRange            = 35,
    FarRange            = 90,
    MaxEngageRange      = 250,

    -- Zamanlama (saniye)
    M1Delay             = 0.35,
    SkillDelay          = 0.8,
    ShunpoDelay         = 2.0,
    ComboDelay          = 0.25,
    DodgeWindow         = 0.4,
    BlockCheckInterval  = 0.1,
    StuckCheckTime      = 3.0,

    -- Davranış
    UseAutoAttack       = true,
    UseAllSkills        = true,
    UseShunpo           = true,
    UseCameraLock       = true,
    UseMovement         = true,
    UseDodge            = true,
    UseBlock            = false,
    SmartCombo          = true,
    AutoRetarget        = true,
    RepositionOnStuck   = true,
    AggressiveMode      = true,

    -- Tuş Atamaları
    SkillKeys           = {"Z","X","C","V","B","G","H","T","R"},
    ShunpoKey           = "Q",
    M1Key               = "Left",
    BlockKey            = "F",
    DashKeys            = {"W","A","S","D"},

    -- Skill Cooldown Tahminleri (saniye)
    SkillCooldowns      = {8, 10, 12, 15, 15, 20, 25, 30, 35},
    M1ComboChain        = 4,

    -- Renk Paleti
    C = {
        BG              = Color3.fromRGB(4,   6,   14),
        Panel           = Color3.fromRGB(10,  14,  22),
        Border          = Color3.fromRGB(0,   200, 255),
        Border2         = Color3.fromRGB(255, 80,  140),
        Accent          = Color3.fromRGB(0,   230, 255),
        Accent2         = Color3.fromRGB(160, 0,   255),
        Green           = Color3.fromRGB(0,   255, 150),
        Red             = Color3.fromRGB(255, 50,  70),
        Orange          = Color3.fromRGB(255, 160, 0),
        Yellow          = Color3.fromRGB(255, 220, 0),
        Text            = Color3.fromRGB(220, 240, 255),
        TextDim         = Color3.fromRGB(100, 130, 170),
        White           = Color3.fromRGB(255, 255, 255),
    }
}

-- ══════════════════════════════════════════════════════════════════
-- GELİŞMİŞ DURUM MAKİNESİ
-- ══════════════════════════════════════════════════════════════════
local State = {
    IDLE            = "IDLE",
    SCANNING        = "SCANNING",
    LOCKING         = "LOCKING",
    APPROACHING     = "APPROACHING",
    DASHING         = "DASHING",
    CLOSE_COMBO     = "CLOSE_COMBO",
    MID_SKILL       = "MID_SKILL",
    LONG_RANGE      = "LONG_RANGE",
    REPOSITIONING   = "REPOSITIONING",
    DODGING         = "DODGING",
    BLOCKING        = "BLOCKING",
    STUCK           = "STUCK",
}

local currentState     = State.IDLE
local previousState    = State.IDLE
local target           = nil
local targetType       = nil
local targetQueue      = {}
local lastM1           = 0
local lastSkill        = 0
local lastShunpo       = 0
local lastDodge        = 0
local lastBlock        = 0
local skillIndex       = 1
local comboCount       = 0
local killCount        = 0
local lastHealth       = humanoid.Health
local combatActive     = true
local targetLocked     = false
local movementActive   = false
local stuckTimer       = 0
local lastPosition     = rootPart.Position
local skillLastUsed    = {}  -- Bireysel skill takibi
local targetHistory    = {}
local dodgeCooldown    = 0
local fpsLastCheck     = 0
local currentFPS       = 60

-- Skill cooldown takibi başlat
for i = 1, #CFG.SkillKeys do
    skillLastUsed[i] = 0
end

-- ══════════════════════════════════════════════════════════════════
-- YARDIMCI FONKSİYONLAR
-- ══════════════════════════════════════════════════════════════════
local function tw(obj, t, props, style, callback)
    if not obj then return end
    pcall(function()
        local tween = TweenService:Create(obj,
            TweenInfo.new(t, style or Enum.EasingStyle.Quart, Enum.EasingDirection.Out),
            props)
        if callback then
            tween.Completed:Connect(callback)
        end
        tween:Play()
    end)
end

local function pressKey(k)
    pcall(function()
        if k == "Left" then
            VIM:SendMouseButtonEvent(0, 0, 0, true)
        else
            local kc = Enum.KeyCode[k]
            if kc then VIM:SendKeyEvent(true, kc, false, game) end
        end
    end)
end

local function releaseKey(k)
    pcall(function()
        if k == "Left" then
            VIM:SendMouseButtonEvent(0, 0, 0, false)
        else
            local kc = Enum.KeyCode[k]
            if kc then VIM:SendKeyEvent(false, kc, false, game) end
        end
    end)
end

local function holdKey(k, duration)
    pressKey(k)
    task.delay(duration or 0.15, function() releaseKey(k) end)
end

local function getRoot(t, tt)
    if not t then return nil end
    if tt == "Player" then
        local char = t.Character
        return char and char:FindFirstChild("HumanoidRootPart")
    end
    return t:FindFirstChild("HumanoidRootPart")
end

local function getHum(t, tt)
    if not t then return nil end
    if tt == "Player" then
        local char = t.Character
        return char and char:FindFirstChild("Humanoid")
    end
    return t:FindFirstChildWhichIsA("Humanoid")
end

local function getDist(t, tt)
    local r = getRoot(t, tt)
    if not r or not rootPart then return math.huge end
    return (rootPart.Position - r.Position).Magnitude
end

local function getHP(t, tt)
    local h = getHum(t, tt)
    if not h then return 0, 100 end
    return h.Health, h.MaxHealth
end

local function isAlive(t, tt)
    local h = getHum(t, tt)
    return h and h.Health > 0
end

local function getVelocity(t, tt)
    local r = getRoot(t, tt)
    if not r then return Vector3.zero end
    return r.Velocity or r.AssemblyLinearVelocity or Vector3.zero
end

-- Gelişmiş NPC Bulma
local function findNPCs()
    local list = {}
    for _, obj in ipairs(Workspace:GetDescendants()) do
        if obj:IsA("Model") and obj ~= character
            and not Players:GetPlayerFromCharacter(obj)
            and obj:FindFirstChildWhichIsA("Humanoid")
            and obj:FindFirstChild("HumanoidRootPart")
        then
            local h = obj:FindFirstChildWhichIsA("Humanoid")
            local r = obj:FindFirstChild("HumanoidRootPart")
            if h and r and h.Health > CFG.MinTargetHealth then
                local d = (rootPart.Position - r.Position).Magnitude
                if d <= CFG.MaxRange then
                    table.insert(list, {obj = obj, dist = d, hp = h.Health, maxHp = h.MaxHealth})
                end
            end
        end
    end
    return list
end

-- FOV Kontrolü
local function isInFOV(targetRoot)
    if not targetRoot or not rootPart then return false end
    local direction  = (targetRoot.Position - rootPart.Position).Unit
    local lookVector = rootPart.CFrame.LookVector
    local dotProduct = lookVector:Dot(direction)
    local angleDeg   = math.deg(math.acos(math.clamp(dotProduct, -1, 1)))
    return angleDeg <= (CFG.FOV_Angle / 2)
end

-- Takım Kontrolü
local function isAlly(t, tt)
    if tt ~= "Player" then return false end
    if not CFG.TargetAllies then
        pcall(function()
            if t.Team and player.Team and t.Team == player.Team then
                return true
            end
        end)
    end
    return false
end

-- Kara Listede mi?
local function isBlacklisted(t, tt)
    local name = tt == "Player" and t.Name or (t and t.Name)
    for _, bl in ipairs(CFG.TargetBlacklist) do
        if bl == name then return true end
    end
    return false
end

-- ══════════════════════════════════════════════════════════════════
-- GELİŞMİŞ HEDEF SİSTEMİ (Priority Queue)
-- ══════════════════════════════════════════════════════════════════
local function scanTargets()
    local candidates = {}

    if CFG.TargetPlayers then
        for _, p in ipairs(Players:GetPlayers()) do
            if p ~= player and p.Character then
                local h = p.Character:FindFirstChild("Humanoid")
                local r = p.Character:FindFirstChild("HumanoidRootPart")
                if h and r and h.Health > CFG.MinTargetHealth
                    and not isAlly(p, "Player")
                    and not isBlacklisted(p, "Player")
                then
                    local d = (rootPart.Position - r.Position).Magnitude
                    if d <= CFG.MaxRange and isInFOV(r) then
                        table.insert(candidates, {
                            target = p,
                            tType  = "Player",
                            dist   = d,
                            hp     = h.Health,
                            maxHp  = h.MaxHealth,
                            root   = r,
                            hum    = h,
                        })
                    end
                end
            end
        end
    end

    if CFG.TargetNPCs then
        for _, npcData in ipairs(findNPCs()) do
            local r = npcData.obj:FindFirstChild("HumanoidRootPart")
            if r and isInFOV(r) and not isBlacklisted(npcData.obj, "NPC") then
                table.insert(candidates, {
                    target = npcData.obj,
                    tType  = "NPC",
                    dist   = npcData.dist,
                    hp     = npcData.hp,
                    maxHp  = npcData.maxHp,
                    root   = r,
                    hum    = npcData.obj:FindFirstChildWhichIsA("Humanoid"),
                })
            end
        end
    end

    if CFG.TargetPriority == "Distance" then
        table.sort(candidates, function(a, b) return a.dist < b.dist end)
    elseif CFG.TargetPriority == "LowHP" then
        table.sort(candidates, function(a, b)
            local ratioA = a.hp / math.max(a.maxHp, 1)
            local ratioB = b.hp / math.max(b.maxHp, 1)
            if math.abs(ratioA - ratioB) < 0.15 then
                return a.dist < b.dist
            end
            return ratioA < ratioB
        end)
    elseif CFG.TargetPriority == "Threat" then
        table.sort(candidates, function(a, b)
            local scoreA = (a.hp / math.max(a.maxHp, 1)) * 50 + (1 / math.max(a.dist, 1)) * 50
            local scoreB = (b.hp / math.max(b.maxHp, 1)) * 50 + (1 / math.max(b.dist, 1)) * 50
            return scoreA > scoreB
        end)
    end

    targetQueue = candidates
    return candidates
end

local function selectBestTarget()
    local candidates = scanTargets()
    if #candidates > 0 then
        local best = candidates[1]
        return best.target, best.tType, best.dist
    end
    return nil, nil, math.huge
end

-- ══════════════════════════════════════════════════════════════════
-- HEDEF KİLİT SİSTEMİ
-- ══════════════════════════════════════════════════════════════════
local function lockTarget(t, tt)
    if not t then return false end
    if isBlacklisted(t, tt) then return false end
    if tt == "Player" and isAlly(t, tt) then return false end
    if not isAlive(t, tt) then return false end

    if target and target ~= t then
        table.insert(targetHistory, {target = target, tType = targetType, time = tick()})
        if #targetHistory > 10 then table.remove(targetHistory, 1) end
    end

    target = t
    targetType = tt
    targetLocked = true
    comboCount = 0
    stuckTimer = 0
    lastPosition = rootPart.Position
    currentState = State.LOCKING
    return true
end

local function clearTarget()
    if target then
        table.insert(targetHistory, {target = target, tType = targetType, time = tick()})
        if #targetHistory > 10 then table.remove(targetHistory, 1) end
    end
    target = nil
    targetType = nil
    targetLocked = false
    comboCount = 0
    currentState = State.SCANNING
    stopMovement()
end

local function cycleTarget(direction)
    if #targetQueue < 2 then return end
    local currentIndex = 0
    for i, candidate in ipairs(targetQueue) do
        if candidate.target == target then
            currentIndex = i
            break
        end
    end
    local newIndex = currentIndex + (direction or 1)
    if newIndex > #targetQueue then newIndex = 1 end
    if newIndex < 1 then newIndex = #targetQueue end
    local newTarget = targetQueue[newIndex]
    if newTarget and isAlive(newTarget.target, newTarget.tType) then
        lockTarget(newTarget.target, newTarget.tType)
    end
end

-- ══════════════════════════════════════════════════════════════════
-- HAREKET SİSTEMİ
-- ══════════════════════════════════════════════════════════════════
local moveConnection = nil
local currentMoveTarget = nil

local function stopMovement()
    movementActive = false
    currentMoveTarget = nil
    if moveConnection then
        moveConnection:Disconnect()
        moveConnection = nil
    end
    pcall(function()
        humanoid:MoveTo(rootPart.Position)
    end)
end

local function moveToTarget(t, tt, desiredDistance)
    if not CFG.UseMovement then return end
    if not t or not isAlive(t, tt) then
        stopMovement()
        return
    end

    local targetRoot = getRoot(t, tt)
    if not targetRoot then
        stopMovement()
        return
    end

    local dist = (rootPart.Position - targetRoot.Position).Magnitude
    desiredDistance = desiredDistance or CFG.CloseRange * 0.7

    if dist <= desiredDistance then
        stopMovement()
        return
    end

    local direction = (targetRoot.Position - rootPart.Position).Unit
    local movePoint = targetRoot.Position - direction * desiredDistance

    movementActive = true
    currentMoveTarget = movePoint
    pcall(function()
        humanoid:MoveTo(movePoint)
    end)
end

-- ══════════════════════════════════════════════════════════════════
-- SIKIŞMA TESPİTİ
-- ══════════════════════════════════════════════════════════════════
local function checkStuck()
    if not target or not movementActive then
        stuckTimer = 0
        lastPosition = rootPart.Position
        return false
    end

    local moved = (rootPart.Position - lastPosition).Magnitude
    if moved < 1.5 then
        stuckTimer = stuckTimer + 0.1
        if stuckTimer >= CFG.StuckCheckTime then
            return true
        end
    else
        stuckTimer = math.max(0, stuckTimer - 0.2)
        lastPosition = rootPart.Position
    end
    return false
end

local function handleStuck()
    if not CFG.RepositionOnStuck then return end
    currentState = State.STUCK
    stopMovement()

    local randomDir = Vector3.new(
        math.random(-100, 100) / 100,
        0,
        math.random(-100, 100) / 100
    ).Unit * 20

    local repositionPoint = rootPart.Position + randomDir
    pcall(function()
        humanoid:MoveTo(repositionPoint)
    end)

    task.wait(0.8)
    stopMovement()
    stuckTimer = 0
    lastPosition = rootPart.Position
    currentState = State.APPROACHING
end

-- ══════════════════════════════════════════════════════════════════
-- KAMERA SİSTEMİ
-- ══════════════════════════════════════════════════════════════════
local cameraLockConn = nil
local cameraSmoothness  = 0.12
local lastCamCFrame     = nil

local function enableCameraLock()
    if cameraLockConn then return end
    lastCamCFrame = Camera.CFrame
    pcall(function()
        Camera.CameraType = Enum.CameraType.Scriptable
    end)

    cameraLockConn = RunService.RenderStepped:Connect(function(dt)
        pcall(function()
            if not target or not combatActive or not CFG.UseCameraLock then
                disableCameraLock()
                return
            end

            local r = getRoot(target, targetType)
            if not r then return end

            local targetPos   = r.Position + Vector3.new(0, 2.5, 0)
            local toTarget    = (targetPos - rootPart.Position).Unit
            local distToTarget= (rootPart.Position - r.Position).Magnitude
            local camDistance = math.clamp(distToTarget * 0.65, 10, 35)
            local camOffset   = Vector3.new(0, 5 + distToTarget * 0.08, 0)
            local desiredPos  = rootPart.Position - toTarget * camDistance + camOffset
            local desiredLook = targetPos

            if lastCamCFrame then
                local smoothPos = lastCamCFrame.Position:Lerp(desiredPos, 1 - math.exp(-dt / cameraSmoothness))
                local smoothLook= lastCamCFrame.LookVector:Lerp((desiredLook - smoothPos).Unit, 1 - math.exp(-dt / cameraSmoothness))
                Camera.CFrame = CFrame.new(smoothPos, smoothPos + smoothLook * 10)
            else
                Camera.CFrame = CFrame.new(desiredPos, desiredLook)
            end
            lastCamCFrame = Camera.CFrame
        end)
    end)
end

local function disableCameraLock()
    if cameraLockConn then
        cameraLockConn:Disconnect()
        cameraLockConn = nil
    end
    lastCamCFrame = nil
    pcall(function()
        Camera.CameraType = Enum.CameraType.Custom
    end)
end

-- ══════════════════════════════════════════════════════════════════
-- SALDIRI SİSTEMİ
-- ══════════════════════════════════════════════════════════════════
local function canUseSkill(index)
    local cd = CFG.SkillCooldowns[index] or 10
    return (tick() - (skillLastUsed[index] or 0)) >= cd
end

local function doM1()
    if not target or not CFG.UseAutoAttack then return end
    if tick() - lastM1 < CFG.M1Delay then return end
    if not isAlive(target, targetType) then return end

    local dist = getDist(target, targetType)
    if dist > CFG.CloseRange then return end

    lastM1 = tick()
    holdKey("Left", 0.08)
    comboCount = math.min(comboCount + 1, CFG.M1ComboChain)
end

local function useSkill(forceIndex)
    if not target or not CFG.UseAllSkills then return end
    if tick() - lastSkill < CFG.SkillDelay then return end
    if not isAlive(target, targetType) then return end

    local idx = forceIndex or skillIndex
    if not canUseSkill(idx) then
        for i = 1, #CFG.SkillKeys do
            local checkIdx = ((idx + i - 1) % #CFG.SkillKeys) + 1
            if canUseSkill(checkIdx) then
                idx = checkIdx
                break
            end
        end
        if not canUseSkill(idx) then return end
    end

    lastSkill = tick()
    local key = CFG.SkillKeys[idx]
    if key then
        skillLastUsed[idx] = tick()
        holdKey(key, 0.1)
        if not forceIndex then
            skillIndex = (idx % #CFG.SkillKeys) + 1
        end
    end
    comboCount = 0
end

local function doShunpo(direction)
    if not CFG.UseShunpo then return end
    if tick() - lastShunpo < CFG.ShunpoDelay then return end
    if not target then return end

    local dist = getDist(target, targetType)

    if direction == "away" then
        pcall(function()
            local targetRoot = getRoot(target, targetType)
            if targetRoot then
                local awayDir = (rootPart.Position - targetRoot.Position).Unit
                local lookPoint = rootPart.Position + awayDir * 20
                Camera.CFrame = CFrame.new(Camera.CFrame.Position, lookPoint)
            end
        end)
    end

    lastShunpo = tick()
    holdKey(CFG.ShunpoKey, 0.12)
end

-- ══════════════════════════════════════════════════════════════════
-- DODGE & BLOCK SİSTEMİ
-- ══════════════════════════════════════════════════════════════════
local function checkIncomingDamage()
    if not target then return false end
    local targetRoot = getRoot(target, targetType)
    if not targetRoot then return false end

    local targetVel  = getVelocity(target, targetType)
    local targetSpeed = targetVel.Magnitude
    local dist        = getDist(target, targetType)

    if targetSpeed > 30 and dist < CFG.CloseRange * 1.5 then
        local approachDot = targetVel.Unit:Dot((rootPart.Position - targetRoot.Position).Unit)
        if approachDot > 0.5 then
            return true, "approach"
        end
    end

    if humanoid.Health < lastHealth - 5 then
        lastHealth = humanoid.Health
        return true, "damaged"
    end

    lastHealth = humanoid.Health
    return false, nil
end

local function performDodge()
    if not CFG.UseDodge then return end
    if tick() - lastDodge < CFG.DodgeWindow * 2 then return end

    currentState  = State.DODGING
    lastDodge     = tick()

    local dodgeDirs = {CFG.DashKeys[2], CFG.DashKeys[3], CFG.DashKeys[4]}
    local dodgeKey  = dodgeDirs[math.random(1, 3)]

    holdKey(dodgeKey, 0.15)
    task.wait(0.05)
    holdKey(CFG.ShunpoKey, 0.1)

    task.wait(0.25)
    currentState = State.APPROACHING
end

local function performBlock()
    if not CFG.UseBlock then return end
    if tick() - lastBlock < CFG.BlockCheckInterval then return end

    lastBlock = tick()
    currentState = State.BLOCKING
    holdKey(CFG.BlockKey, 0.25)
    task.wait(0.3)
    if currentState == State.BLOCKING then
        currentState = State.APPROACHING
    end
end

-- ══════════════════════════════════════════════════════════════════
-- DURUM GÜNCELLEME
-- ══════════════════════════════════════════════════════════════════
local function updateCombatState()
    if not combatActive then
        currentState = State.IDLE
        return
    end

    if not target or not isAlive(target, targetType) then
        if targetLocked then clearTarget() end
        currentState = State.SCANNING
        return
    end

    local dist       = getDist(target, targetType)
    local incoming, reason = checkIncomingDamage()

    if incoming and CFG.UseDodge and tick() - lastDodge > 1.5 then
        if reason == "approach" or reason == "damaged" then
            if humanoid.Health / humanoid.MaxHealth < 0.35 then
                performDodge()
                return
            end
        end
    end

    if checkStuck() then
        handleStuck()
        return
    end

    if dist <= CFG.KillAuraRange then
        currentState = State.CLOSE_COMBO
    elseif dist <= CFG.CloseRange then
        currentState = State.CLOSE_COMBO
    elseif dist <= CFG.MidRange then
        currentState = State.MID_SKILL
    elseif dist <= CFG.FarRange then
        currentState = State.APPROACHING
    elseif dist <= CFG.MaxEngageRange then
        currentState = State.LONG_RANGE
    else
        currentState = State.SCANNING
        clearTarget()
    end

    previousState = currentState
end

-- ══════════════════════════════════════════════════════════════════
-- DURUM EYLEMLERİ
-- ══════════════════════════════════════════════════════════════════
local function executeState()
    if not combatActive then return end

    if target and not isAlive(target, targetType) then
        killCount = killCount + 1
        clearTarget()
        if CFG.AutoRetarget then
            task.wait(CFG.RetargetDelay)
            local t, tt = selectBestTarget()
            if t then lockTarget(t, tt) end
        end
        return
    end

    if currentState == State.SCANNING then
        stopMovement()
        local t, tt, d = selectBestTarget()
        if t and d < CFG.MaxRange then
            lockTarget(t, tt)
            enableCameraLock()
        end
    elseif currentState == State.LOCKING then
        if not target then return end
        local dist = getDist(target, targetType)
        if dist > CFG.CloseRange then
            moveToTarget(target, targetType, CFG.CloseRange * 0.7)
        end
        currentState = State.APPROACHING
    elseif currentState == State.APPROACHING then
        if not target then return end
        local dist = getDist(target, targetType)
        if dist > CFG.CloseRange * 1.2 then
            moveToTarget(target, targetType, CFG.CloseRange * 0.6)
            if CFG.UseShunpo and dist > CFG.MidRange and tick() - lastShunpo > CFG.ShunpoDelay then
                doShunpo("toward")
            end
        else
            stopMovement()
        end
        if dist <= CFG.MidRange then
            doM1()
        end
    elseif currentState == State.CLOSE_COMBO then
        stopMovement()
        if not target then return end
        local dist = getDist(target, targetType)
        if dist > CFG.CloseRange * 1.3 then
            currentState = State.APPROACHING
            return
        end
        if comboCount < CFG.M1ComboChain then
            doM1()
        else
            useSkill()
        end
        if dist <= CFG.KillAuraRange and tick() - lastM1 > CFG.M1Delay * 0.8 then
            doM1()
        end
    elseif currentState == State.MID_SKILL then
        stopMovement()
        if not target then return end
        local dist = getDist(target, targetType)
        if dist > CFG.MidRange * 1.2 then
            currentState = State.APPROACHING
            return
        end
        if tick() - lastSkill > CFG.SkillDelay * 0.6 then
            useSkill()
        end
        if dist < CFG.CloseRange then
            doM1()
        end
    elseif currentState == State.LONG_RANGE then
        if not target then return end
        if CFG.UseShunpo and tick() - lastShunpo > CFG.ShunpoDelay * 0.5 then
            doShunpo("toward")
        else
            moveToTarget(target, targetType, CFG.MidRange)
        end
    elseif currentState == State.STUCK then
        if not checkStuck() then
            currentState = State.APPROACHING
        end
    end
end

-- ══════════════════════════════════════════════════════════════════
-- UI OLUŞTUR (GARANTİLİ GÖRÜNÜM)
-- ══════════════════════════════════════════════════════════════════
local function createUI()
    local SG = Instance.new("ScreenGui")
    SG.Name = "AUT_COMBAT_OMEGA_V2"
    SG.ResetOnSpawn = false
    SG.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    SG.IgnoreGuiInset = true
    SG.ZIndex = 100

    -- Güvenli parent
    local parentSuccess, parentResult = pcall(function()
        local pg = player:WaitForChild("PlayerGui")
        SG.Parent = pg
        return pg
    end)
    if not parentSuccess then
        pcall(function()
            SG.Parent = game:GetService("CoreGui")
        end)
        print("⚠ PlayerGui alınamadı, CoreGui kullanıldı")
    else
        print("✅ UI parent: " .. parentResult.Name)
    end

    local function New(className, parent, properties)
        local obj = Instance.new(className)
        if parent then obj.Parent = parent end
        for key, value in pairs(properties or {}) do
            obj[key] = value
        end
        return obj
    end

    -- Ana Panel (boyut sabit)
    local Main = New("Frame", SG, {
        Name = "MainPanel",
        BackgroundColor3 = CFG.C.BG,
        BorderSizePixel = 0,
        Size = UDim2.new(0, 280, 0, 470),
        Position = UDim2.new(0, 20, 0, 20),
        BackgroundTransparency = 0.06,
        Visible = true,
    })
    New("UICorner", Main, {CornerRadius = UDim.new(0, 10)})
    local mainStroke = New("UIStroke", Main, {
        Color = CFG.C.Border,
        Thickness = 1.8,
        Transparency = 0.15,
    })

    New("UIPadding", Main, {
        PaddingTop    = UDim.new(0, 14),
        PaddingBottom = UDim.new(0, 14),
        PaddingLeft   = UDim.new(0, 14),
        PaddingRight  = UDim.new(0, 14),
    })

    local Inner = New("Frame", Main, {
        BackgroundTransparency = 1,
        Size = UDim2.new(1, -28, 1, -28),
    })

    local listLayout = New("UIListLayout", Inner, {
        SortOrder = Enum.SortOrder.LayoutOrder,
        Padding   = UDim.new(0, 10),
    })

    -- Başlık
    local TitleFrame = New("Frame", Inner, {
        Size = UDim2.new(1, 0, 0, 26),
        BackgroundTransparency = 1,
        LayoutOrder = 1,
    })
    New("TextLabel", TitleFrame, {
        Size = UDim2.new(0.7, 0, 1, 0),
        BackgroundTransparency = 1,
        Text = "⚔ OMEGA COMBAT v2.0",
        TextColor3 = CFG.C.Accent,
        TextSize = 13,
        Font = Enum.Font.GothamBold,
        TextXAlignment = Enum.TextXAlignment.Left,
    })
    local KillsLabel = New("TextLabel", TitleFrame, {
        Size = UDim2.new(0.3, 0, 1, 0),
        BackgroundTransparency = 1,
        Text = "☠ 0",
        TextColor3 = CFG.C.Orange,
        TextSize = 10,
        Font = Enum.Font.GothamBold,
        TextXAlignment = Enum.TextXAlignment.Right,
        Position = UDim2.new(0.7, 0, 0, 0),
    })

    -- Hedef Paneli
    local TargetFrame = New("Frame", Inner, {
        Size = UDim2.new(1, 0, 0, 80),
        BackgroundColor3 = CFG.C.Panel,
        BorderSizePixel = 0,
        LayoutOrder = 2,
    })
    New("UICorner", TargetFrame, {CornerRadius = UDim.new(0, 8)})
    New("UIStroke", TargetFrame, {Color = CFG.C.Border, Thickness = 1, Transparency = 0.35})
    New("UIPadding", TargetFrame, {PaddingAll = UDim.new(0, 10)})

    local targetInnerLayout = New("UIListLayout", TargetFrame, {
        SortOrder = Enum.SortOrder.LayoutOrder,
        Padding   = UDim.new(0, 5),
    })
    local TargetLabel = New("TextLabel", TargetFrame, {
        Size = UDim2.new(1, 0, 0, 16),
        BackgroundTransparency = 1,
        Text = "🎯 NO TARGET LOCKED",
        TextColor3 = CFG.C.Text,
        TextSize = 11,
        Font = Enum.Font.GothamBold,
        TextXAlignment = Enum.TextXAlignment.Left,
        LayoutOrder = 1,
    })
    local HPFrame = New("Frame", TargetFrame, {
        Size = UDim2.new(1, 0, 0, 18),
        BackgroundColor3 = Color3.fromRGB(20, 20, 30),
        BorderSizePixel = 0,
        LayoutOrder = 2,
    })
    New("UICorner", HPFrame, {CornerRadius = UDim.new(0, 4)})
    local HPBar = New("Frame", HPFrame, {
        Size = UDim2.new(0, 0, 1, 0),
        BackgroundColor3 = CFG.C.Green,
        BorderSizePixel = 0,
    })
    New("UICorner", HPBar, {CornerRadius = UDim.new(0, 4)})
    local HPGlow = New("Frame", HPFrame, {
        Size = UDim2.new(0, 0, 1, 0),
        BackgroundColor3 = CFG.C.Green,
        BackgroundTransparency = 0.7,
        BorderSizePixel = 0,
    })
    New("UICorner", HPGlow, {CornerRadius = UDim.new(0, 4)})
    local HPLabel = New("TextLabel", HPFrame, {
        Size = UDim2.new(1, -6, 1, 0),
        BackgroundTransparency = 1,
        Text = "HP: --/--",
        TextColor3 = CFG.C.Text,
        TextSize = 9,
        Font = Enum.Font.GothamBold,
        Position = UDim2.new(0, 3, 0, 0),
        ZIndex = 2,
    })
    local DistLabel = New("TextLabel", TargetFrame, {
        Size = UDim2.new(1, 0, 0, 13),
        BackgroundTransparency = 1,
        Text = "📏 0.0m | ⚡ --",
        TextColor3 = CFG.C.TextDim,
        TextSize = 9,
        Font = Enum.Font.Gotham,
        TextXAlignment = Enum.TextXAlignment.Left,
        LayoutOrder = 3,
    })

    -- Durum Paneli
    local StateFrame = New("Frame", Inner, {
        Size = UDim2.new(1, 0, 0, 72),
        BackgroundColor3 = CFG.C.Panel,
        BorderSizePixel = 0,
        LayoutOrder = 3,
    })
    New("UICorner", StateFrame, {CornerRadius = UDim.new(0, 8)})
    New("UIStroke", StateFrame, {Color = CFG.C.Border2, Thickness = 1, Transparency = 0.3})
    New("UIPadding", StateFrame, {PaddingAll = UDim.new(0, 10)})

    local stateLayout = New("UIListLayout", StateFrame, {
        SortOrder = Enum.SortOrder.LayoutOrder,
        Padding   = UDim.new(0, 4),
    })
    local StateLabel = New("TextLabel", StateFrame, {
        Size = UDim2.new(1, 0, 0, 20),
        BackgroundTransparency = 1,
        Text = "◈ IDLE",
        TextColor3 = CFG.C.TextDim,
        TextSize = 12,
        Font = Enum.Font.GothamBold,
        TextXAlignment = Enum.TextXAlignment.Left,
        LayoutOrder = 1,
    })
    local ComboLabel = New("TextLabel", StateFrame, {
        Size = UDim2.new(1, 0, 0, 14),
        BackgroundTransparency = 1,
        Text = "COMBO: 0x | ⏳ --",
        TextColor3 = CFG.C.Orange,
        TextSize = 10,
        Font = Enum.Font.Gotham,
        TextXAlignment = Enum.TextXAlignment.Left,
        LayoutOrder = 2,
    })
    local SkillCDFrame = New("Frame", StateFrame, {
        Size = UDim2.new(1, 0, 0, 8),
        BackgroundTransparency = 0.85,
        BackgroundColor3 = Color3.fromRGB(30, 30, 40),
        BorderSizePixel = 0,
        LayoutOrder = 3,
    })
    New("UICorner", SkillCDFrame, {CornerRadius = UDim.new(0, 2)})
    local SkillCDBar = New("Frame", SkillCDFrame, {
        Size = UDim2.new(1, 0, 1, 0),
        BackgroundColor3 = CFG.C.Accent,
        BackgroundTransparency = 0.4,
        BorderSizePixel = 0,
    })
    New("UICorner", SkillCDBar, {CornerRadius = UDim.new(0, 2)})

    -- Butonlar
    local BtnRow1 = New("Frame", Inner, {
        Size = UDim2.new(1, 0, 0, 30),
        BackgroundTransparency = 1,
        LayoutOrder = 4,
    })
    local btnList1 = New("UIListLayout", BtnRow1, {
        SortOrder = Enum.SortOrder.LayoutOrder,
        FillDirection = Enum.FillDirection.Horizontal,
        Padding = UDim.new(0, 5),
    })

    local function mkBtn(text, color, parent, callback)
        local btn = New("TextButton", parent, {
            Text = text,
            TextColor3 = CFG.C.Text,
            TextSize = 9,
            Font = Enum.Font.GothamBold,
            BackgroundColor3 = color,
            BorderSizePixel = 0,
            Size = UDim2.new(0.33, -3, 1, 0),
            AutoButtonColor = false,
        })
        New("UICorner", btn, {CornerRadius = UDim.new(0, 5)})
        New("UIStroke", btn, {Color = color, Thickness = 0.6, Transparency = 0.3})
        btn.MouseEnter:Connect(function()
            tw(btn, 0.1, {BackgroundTransparency = 0.2})
        end)
        btn.MouseLeave:Connect(function()
            tw(btn, 0.15, {BackgroundTransparency = 0})
        end)
        btn.MouseButton1Click:Connect(function()
            tw(btn, 0.06, {BackgroundTransparency = 0.4})
            task.wait(0.06)
            tw(btn, 0.08, {BackgroundTransparency = 0})
            callback()
        end)
        return btn
    end

    local masterActive = true
    local masterBtn = mkBtn("⚡ ACTIVE", CFG.C.Green, BtnRow1, function()
        masterActive = not masterActive
        combatActive = masterActive
        if masterActive then
            tw(masterBtn, 0.25, {BackgroundColor3 = CFG.C.Green})
            masterBtn.Text = "⚡ ACTIVE"
            tw(mainStroke, 0.25, {Color = CFG.C.Border})
        else
            tw(masterBtn, 0.25, {BackgroundColor3 = CFG.C.Red})
            masterBtn.Text = "⏸ PAUSED"
            tw(mainStroke, 0.25, {Color = CFG.C.Red})
            clearTarget()
            disableCameraLock()
            stopMovement()
        end
    end)

    mkBtn("🔄 SWITCH", CFG.C.Accent2, BtnRow1, function()
        cycleTarget(1)
    end)

    mkBtn("❌ CLEAR", CFG.C.Orange, BtnRow1, function()
        clearTarget()
        disableCameraLock()
        stopMovement()
    end)

    local BtnRow2 = New("Frame", Inner, {
        Size = UDim2.new(1, 0, 0, 28),
        BackgroundTransparency = 1,
        LayoutOrder = 5,
    })
    local btnList2 = New("UIListLayout", BtnRow2, {
        SortOrder = Enum.SortOrder.LayoutOrder,
        FillDirection = Enum.FillDirection.Horizontal,
        Padding = UDim.new(0, 5),
    })

    mkBtn("🛡 DODGE", CFG.C.Yellow, BtnRow2, function()
        performDodge()
    end)

    mkBtn("💠 SHUNPO", CFG.C.Accent, BtnRow2, function()
        doShunpo("toward")
    end)

    mkBtn("✕ CLOSE", CFG.C.Red, BtnRow2, function()
        clearTarget()
        disableCameraLock()
        stopMovement()
        SG:Destroy()
    end)

    New("TextLabel", Inner, {
        Size = UDim2.new(1, 0, 0, 14),
        BackgroundTransparency = 1,
        Text = "◆ OMEGA ENGINE • FPS: 60",
        TextColor3 = CFG.C.TextDim,
        TextSize = 8,
        Font = Enum.Font.Gotham,
        TextXAlignment = Enum.TextXAlignment.Left,
        LayoutOrder = 6,
    })

    -- UI Güncelleme Fonksiyonu
    local function updateUI()
        if target and targetLocked and isAlive(target, targetType) then
            local hp, maxhp  = getHP(target, targetType)
            local ratio      = math.clamp(hp / math.max(maxhp, 1), 0, 1)
            local hpColor    = ratio > 0.5 and CFG.C.Green or (ratio > 0.25 and CFG.C.Yellow or CFG.C.Red)
            local dist       = getDist(target, targetType)
            local targetName = targetType == "Player" and target.Name or (target.Name or "NPC")
            local vel        = getVelocity(target, targetType).Magnitude

            tw(HPBar, 0.2, {Size = UDim2.new(ratio, 0, 1, 0), BackgroundColor3 = hpColor})
            tw(HPGlow, 0.2, {Size = UDim2.new(ratio, 0, 1, 0), BackgroundColor3 = hpColor})
            HPLabel.Text = string.format("HP: %.0f/%.0f (%.0f%%)", hp, maxhp, ratio * 100)
            TargetLabel.Text = "🎯 " .. string.sub(targetName, 1, 22)
            DistLabel.Text = string.format("📏 %.1fm | ⚡ %.0f u/s", dist, vel)
        else
            TargetLabel.Text = "🎯 NO TARGET"
            HPLabel.Text    = "HP: --/--"
            DistLabel.Text  = "📏 -- | ⚡ --"
            tw(HPBar, 0.15, {Size = UDim2.new(0, 0, 1, 0)})
            tw(HPGlow, 0.15, {Size = UDim2.new(0, 0, 1, 0)})
        end

        local stateIcons = {
            [State.IDLE]          = "◈ IDLE",
            [State.SCANNING]      = "🔍 SCANNING",
            [State.LOCKING]       = "🔒 LOCKING",
            [State.APPROACHING]   = "▶ APPROACHING",
            [State.DASHING]       = "💨 DASHING",
            [State.CLOSE_COMBO]   = "⚔ IN COMBAT",
            [State.MID_SKILL]     = "✦ CASTING",
            [State.LONG_RANGE]    = "➤ CHASING",
            [State.REPOSITIONING] = "↻ REPOSITION",
            [State.DODGING]       = "↗ EVADING",
            [State.BLOCKING]      = "🛡 BLOCKING",
            [State.STUCK]         = "⚠ UNSTUCK",
        }
        local stateColors = {
            [State.IDLE]          = CFG.C.TextDim,
            [State.SCANNING]      = CFG.C.TextDim,
            [State.LOCKING]       = CFG.C.Accent2,
            [State.APPROACHING]   = CFG.C.Orange,
            [State.DASHING]       = CFG.C.Accent,
            [State.CLOSE_COMBO]   = CFG.C.Green,
            [State.MID_SKILL]     = CFG.C.Accent or CFG.Accent,
            [State.LONG_RANGE]    = CFG.C.Yellow,
            [State.REPOSITIONING] = CFG.C.Orange,
            [State.DODGING]       = CFG.C.Yellow,
            [State.BLOCKING]      = CFG.C.Accent,
            [State.STUCK]         = CFG.C.Red,
        }
        StateLabel.Text = stateIcons[currentState] or "◈ UNKNOWN"
        tw(StateLabel, 0.1, {TextColor3 = stateColors[currentState] or CFG.C.TextDim})

        local nextSkillReady = canUseSkill(skillIndex)
        local cdRemaining    = CFG.SkillCooldowns[skillIndex] - (tick() - (skillLastUsed[skillIndex] or 0))
        ComboLabel.Text = string.format("COMBO: %dx | SKILL[%d]: %s", comboCount, skillIndex,
            nextSkillReady and "READY" or string.format("%.1fs", math.max(0, cdRemaining)))

        local minCD = math.huge
        local maxCD = 0
        for i = 1, #CFG.SkillKeys do
            local remaining = CFG.SkillCooldowns[i] - (tick() - (skillLastUsed[i] or 0))
            minCD = math.min(minCD, remaining)
            maxCD = math.max(maxCD, CFG.SkillCooldowns[i])
        end
        local cdRatio = math.clamp(1 - (minCD / math.max(maxCD, 1)), 0, 1)
        tw(SkillCDBar, 0.2, {Size = UDim2.new(cdRatio, 0, 1, 0)})

        KillsLabel.Text = "☠ " .. killCount
    end

    return SG, updateUI
end

-- ══════════════════════════════════════════════════════════════════
-- UI'Yİ BAŞLAT
-- ══════════════════════════════════════════════════════════════════
print("🎨 UI oluşturuluyor...")
local SG, updateUI = createUI()
print("✅ OMEGA UI başarıyla yüklendi!")

-- ══════════════════════════════════════════════════════════════════
-- KARAKTER YENİLENME
-- ══════════════════════════════════════════════════════════════════
player.CharacterAdded:Connect(function(newChar)
    character = newChar
    humanoid  = newChar:WaitForChild("Humanoid")
    rootPart  = newChar:WaitForChild("HumanoidRootPart")
    lastHealth = humanoid.Health
    clearTarget()
    disableCameraLock()
    stopMovement()
    stuckTimer   = 0
    lastPosition = rootPart.Position
end)

-- ══════════════════════════════════════════════════════════════════
-- KLAVYE KISAYOLLARI
-- ══════════════════════════════════════════════════════════════════
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.Y then
        cycleTarget(1)
    elseif input.KeyCode == Enum.KeyCode.U then
        cycleTarget(-1)
    elseif input.KeyCode == Enum.KeyCode.P then
        performDodge()
        task.wait(0.3)
        clearTarget()
        disableCameraLock()
        stopMovement()
    end
end)

-- ══════════════════════════════════════════════════════════════════
-- ANA OYUN DÖNGÜSÜ
-- ══════════════════════════════════════════════════════════════════
task.spawn(function()
    local uiUpdateCounter   = 0
    local stateUpdateCounter= 0
    local fpsFrameCount     = 0
    local fpsLastTime       = tick()

    while SG and SG.Parent do
        local dt = task.wait(0.05)

        pcall(function()
            fpsFrameCount = fpsFrameCount + 1
            if tick() - fpsLastTime >= 1.0 then
                currentFPS = fpsFrameCount
                fpsFrameCount = 0
                fpsLastTime = tick()
            end

            if not combatActive or not character or not character.Parent then
                stopMovement()
                return
            end

            if not humanoid or humanoid.Health <= 0 then
                clearTarget()
                disableCameraLock()
                stopMovement()
                return
            end

            if target then
                if not isAlive(target, targetType) then
                    killCount = killCount + 1
                    clearTarget()
                    disableCameraLock()
                    stopMovement()
                end
            end

            if not target or not targetLocked then
                local t, tt, d = selectBestTarget()
                if t and d < CFG.MaxRange then
                    lockTarget(t, tt)
                    enableCameraLock()
                end
            end

            stateUpdateCounter = stateUpdateCounter + 1
            if stateUpdateCounter >= 2 then
                stateUpdateCounter = 0
                updateCombatState()
            end

            executeState()

            uiUpdateCounter = uiUpdateCounter + 1
            if uiUpdateCounter >= 5 then
                uiUpdateCounter = 0
                updateUI()
            end
        end)
    end
end)

-- ══════════════════════════════════════════════════════════════════
-- BAŞLANGIÇ MESAJI
-- ══════════════════════════════════════════════════════════════════
print(string.rep("═", 60))
print("  ⚔ OMEGA COMBAT SYSTEM v2.0 — AKTİF ⚔")
print("  ◆ Neural Target Lock     ◆ Adaptive Combat AI")
print("  ◆ Frame-Perfect Combos    ◆ Smart Dodge System")
print("  ◆ Movement Engine         ◆ Kill Aura Detection")
print("  ◆ Priority Target Queue   ◆ Anti-Stuck Recovery")
print("  ◆ Skill CD Tracker        ◆ Pro Camera System")
print(string.rep("═", 60))
print("  KISAYOLLAR: [Y] Next Target | [U] Prev Target")
print("              [P] Panic Dodge + Escape")
print(string.rep("═", 60))
